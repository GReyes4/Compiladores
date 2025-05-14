# Analizador semántico

from EstructurasSemanticas import FunctionDirectory  # Importa las estructuras de datos
from CuboSemantico import check_semantic          # Importa el cubo semántico


class SemanticAnalyzer:
    def __init__(self):
        self.function_directory = FunctionDirectory()
        self.current_function = None  # Para rastrear la función actual

    def analyze(self, tree):
        """Analiza el árbol sintáctico para llenar el Directorio de Funciones y validar tipos."""
        for child in tree.children:
            if child.data == "programa":
                self._process_program(child)
            elif child.data == "vars":
                self._process_vars(child)
            elif child.data == "funcs":
                self._process_funcs(child)
            elif child.data == "body":
                self._process_body(child)

    def _process_program(self, tree):
        """Procesa la declaración del programa principal."""
        program_name = tree.children[0].value
        self.function_directory.add_function(program_name, "VOID")
        self.current_function = program_name

    def _process_vars(self, tree):
        """Procesa las declaraciones de variables."""
        for var_decl in tree.children:
            var_name = var_decl.children[0].value
            var_type = var_decl.children[1].value
            self.function_directory.add_variable_to_function(self.current_function, var_name, var_type)

    def _process_funcs(self, tree):
        """Procesa las declaraciones de funciones."""
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
        for statement in tree.children:
            if statement.data == "asignacion":
                self._process_asignacion(statement)
            elif statement.data == "print":
                self._process_print(statement)

    def _process_asignacion(self, tree):
        """Valida la asignación de variables."""
        var_name = tree.children[0].value
        var_type = self.function_directory.get_variable_type_in_function(self.current_function, var_name)

        # Obtener el tipo del valor asignado
        value_node = tree.children[1]
        value_type = self._get_expression_type(value_node)

        # Validar la asignación usando el cubo semántico
        check_semantic("=", var_type, value_type)

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
        if node.type == "ID":
            return self.function_directory.get_variable_type_in_function(self.current_function, node.value)
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
            return check_semantic(operator, left_type, right_type)
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