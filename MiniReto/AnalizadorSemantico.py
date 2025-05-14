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
        else:
            raise ValueError(f"Tipo de nodo no reconocido: {node}")