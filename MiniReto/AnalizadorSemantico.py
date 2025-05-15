# Analizador semántico
from lark import Tree, Token
from EstructurasSemanticas import FunctionDirectory  # Importa las estructuras de datos
from CuboSemantico import check_semantic          # Importa el cubo semántico
from RepresentacionCuadruplos import QuadrupleGenerator # Importa el generador de cuádruplos


class SemanticAnalyzer:
    def __init__(self):
        self.function_directory = FunctionDirectory()
        self.current_function = None  # Para rastrear la función actual
        self.quad_generator = QuadrupleGenerator()

    def analyze(self, tree):
        """Analiza el árbol sintáctico para llenar el Directorio de Funciones y validar tipos."""
        #print(tree.pretty())

        if not tree.children:
            raise ValueError("El árbol sintáctico está vacío.")
        
        # Procesar el nodo 'programa'
        programa_node = tree.children[0]
        if programa_node.data != "programa":
            raise ValueError(f"Se esperaba un nodo 'programa', pero se encontró '{programa_node.data}'.")
        
        self._process_program(programa_node)

        # Iterar sobre los nodos internos de 'programa'
        for child in programa_node.children:
            if isinstance(child, Tree):  # Asegurar que sea un nodo del árbol
                if child.data == "vars":
                    self._process_vars(child)
                elif child.data == "funcs":
                    self._process_funcs(child)
                elif child.data == "body":
                    self._process_body(child)
            else:
                print(f"Token ignorado: {child.type} ({child.value})")

    def _process_program(self, tree):
        """Procesa la declaración del programa principal."""
        #print("tree en process_program:", tree)
        program_name = tree.children[0].value
        self.function_directory.add_function(program_name, "VOID")
        self.current_function = program_name

    def _process_vars(self, tree):
        """Procesa las declaraciones de variables."""
        print("Procesando variables...")
        var_names = []
        var_type = None

        for child in tree.children:
            if isinstance(child, Tree):  # Procesar solo nodos del árbol
                print("child en process_vars:", child)
                if child.data == "ids":  # Nodo 'ids' contiene los nombres de las variables
                    var_names = self._extract_ids(child)  # Extraer los nombres de las variables
                    print("var_names:", var_names)
                elif child.data == "type":  # Nodo 'type' contiene el tipo de las variables
                    var_type = child.children[0].value  # Obtener el tipo (INT o FLOAT)
                    print("var_type:", var_type)
            else:
                print(f"Token ignorado: {child.type} ({child.value})")  # Mensaje más descriptivo

        # Validar que se haya encontrado un tipo
        if not var_type:
            raise ValueError("Error semántico: Tipo de variable no especificado.")

        # Agregar las variables al directorio de funciones
        for var_name in var_names:
            try:
                self.function_directory.add_variable_to_function(self.current_function, var_name, var_type)
            except ValueError as e:
                print(e)  # Imprimir el error detallado
                raise  # Relanzar el error para detener el análisis

    def _extract_ids(self, ids_node):
        """Extrae los nombres de las variables de un nodo 'ids'."""
        var_names = []
        current = ids_node
        print("ids_node en extract_ids:", ids_node)

        while current:
            # Procesar el primer hijo (puede ser un token o un nodo)
            print("current en extract_ids:", current)
            print("current.children:", current.children)

            # Verificar si hay elementos en current.children
            if not current.children:
                break

            if isinstance(current.children[0], Token) and current.children[0].type == "ID":
                var_name = current.children[0].value
                var_names.append(var_name)
                print("ID encontrado:", var_name)

            # Verificar si hay más IDs en el nodo 'com'
            if len(current.children) > 1 and isinstance(current.children[1], Tree) and current.children[1].data == "com":
                current = current.children[1]  # Avanzar al siguiente ID
            else:
                break

        return var_names

    def _process_funcs(self, tree):
        """Procesa las declaraciones de funciones."""
        #print("tree en process_funcs:", tree)
        for func_decl in tree.children:
            func_name = func_decl.children[0].value
            return_type = func_decl.children[1].value
            self.function_directory.add_function(func_name, return_type)
            self.current_function = func_name

            # Procesar las variables locales de la función
            vars_node = func_decl.children[2]
            self._process_vars(vars_node)

    def _process_body(self, tree):
        """Procesa el cuerpo de una función."""
        #print("Cuerpo de la función:", tree.children)
        for child in tree.children:
            #print("child en process_body:", child)
            if isinstance(child, Tree):  # Procesar solo nodos del árbol
                if child.data == "asignacion":
                    self._process_asignacion(child)
                elif child.data == "print":
                    self._process_print(child)
                elif child.data == "condition":
                    self._process_condition(child)
                elif child.data == "cycle":
                    self._process_cycle(child)
                elif child.data == "f_call":
                    self._process_f_call(child)
            else:
                print(f"Elemento ignorado: {child}")  # Ignorar tokens

    def _process_asignacion(self, tree):
        """Valida la asignación de variables."""
        print("Asignación del tree.children:", tree.children)
        var_name = tree.children[0].value
        print("var_name:", var_name)
        var_type = self.function_directory.get_variable_type_in_function(self.current_function, var_name)
        print("var_type:", var_type)

        # Obtener el tipo del valor asignado
        value_node = tree.children[1]
        print("value_node:", value_node)
        value_type = self._get_expression_type(value_node)
        print("value_type:", value_type)

        # Validar la asignación usando el cubo semántico
        print(check_semantic("=", var_type, value_type))

    def _process_condition(self, tree):
        """Valida la instrucción IF."""
        # Obtener la expresión condicional
        condition_node = tree.children[0]
        condition_type = self._get_expression_type(condition_node)

        # Verificar que la expresión sea de tipo BOOL implícito
        if condition_type != "BOOL":
            raise TypeError(f"Error semántico: La expresión condicional debe ser de tipo booleano implícito, pero es de tipo {condition_type}.")

        # Procesar el cuerpo del IF
        then_body = tree.children[1]
        self._process_body(then_body)

        # Si hay un ELSE, procesar su cuerpo
        if len(tree.children) == 3:
            else_body = tree.children[2]
            self._process_body(else_body)

    def _process_cycle(self, tree):
        """Valida la instrucción WHILE."""
        # Obtener la expresión condicional
        condition_node = tree.children[0]
        condition_type = self._get_expression_type(condition_node)

        # Verificar que la expresión sea de tipo BOOL implícito
        if condition_type != "BOOL":
            raise TypeError(f"Error semántico: La expresión condicional debe ser de tipo booleano implícito, pero es de tipo {condition_type}.")

        # Procesar el cuerpo del ciclo
        body = tree.children[1]
        self._process_body(body)

    def _process_f_call(self, tree):
        """Valida la llamada a una función."""
        func_name = tree.children[0].value

        try:
            function_info = self.function_directory.get_function(func_name)
        except ValueError as e:
            raise NameError(f"Error semántico: La función '{func_name}' no está definida.") from e

        args_nodes = tree.children[1:]
        args_types = [self._get_expression_type(arg) for arg in args_nodes]

        param_types = function_info["variable_table"].get_variable_types()
        if len(args_types) != len(param_types):
            raise TypeError(f"Error semántico: La función '{func_name}' espera {len(param_types)} argumentos, pero se proporcionaron {len(args_types)}.")
        
        for arg_type, param_type in zip(args_types, param_types):
            if arg_type != param_type:
                raise TypeError(f"Error semántico: El tipo del argumento no coincide con el tipo del parámetro.")


    def _process_print(self, tree):
        """Valida la instrucción PRINT."""
        print_value = tree.children[0]
        self._get_expression_type(print_value)

    def _get_expression_type(self, node):
        """Obtiene el tipo de una expresión."""
        print("get_expression_type del nodo: ", node)
        print("node.type: ", node.type)
        print("node.data: ", node.data)
        if node.type == "ID":
            try:
                return self.function_directory.get_variable_type_in_function(self.current_function, node.value)
            except ValueError as e:
                print(e)  # Imprimir el error detallado
                raise  # Relanzar el error para detener el análisis
        elif node.type == "CTE_INT":
            return "INT"
        elif node.type == "CTE_FLOAT":
            return "FLOAT"
        elif node.type == "STRING":
            return "STRING"
        elif node.data in ["+", "-", "*", "/"]:
            left_type = self._get_expression_type(node.children[0])
            right_type = self._get_expression_type(node.children[1])
            operator = node.data
            # Validar tipos usando el cubo semántico
            result_type = check_semantic(operator, left_type, right_type)

            # Generar un cuádruplo para la operación
            temp_var = self.quad_generator.generate_temp()
            self.quad_generator.add_quadruple(operator, left_type, right_type, temp_var)

            # Agregar el resultado a la pila de operandos
            self.quad_generator.operand_stack.append(temp_var)
            self.quad_generator.type_stack.append(result_type)

            return result_type
        elif node.data in ["<", ">", "!="]:
            left_type = self._get_expression_type(node.children[0])
            right_type = self._get_expression_type(node.children[1])
            operator = node.data
            result_type = check_semantic(operator, left_type, right_type)
            if result_type != "BOOL":
                raise TypeError(f"Error semántico: La operación '{operator}' debe devolver un tipo booleano implícito.")
            return "BOOL"
        else:
            raise ValueError(f"Tipo de nodo no reconocido: {node}")
