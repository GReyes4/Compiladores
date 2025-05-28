# Estructuras semánticas de Tabla de Variables y Directorio de Funciones

class VariableTable:
    def __init__(self):
        self.variables = {}

    def add_variable(self, var_name, var_type):
        if var_name in self.variables:
            raise ValueError(f"Error semántico: La variable '{var_name}' ya está declarada.")
        self.variables[var_name] = var_type
        print(f"Variable '{var_name}' de tipo '{var_type}' añadida a la tabla de variables.")

    def get_variable_type(self, var_name):
        if var_name not in self.variables:
            raise ValueError(f"Error semántico: La variable '{var_name}' no está declarada.")
        return self.variables[var_name]


class FunctionDirectory:
    def __init__(self):
        self.functions = {}

    def add_function(self, func_name, return_type):
        if func_name in self.functions:
            raise ValueError(f"Error semántico: La función '{func_name}' ya está declarada.")
        self.functions[func_name] = {
            "return_type": return_type,
            "variable_table": VariableTable()
        }

    def get_function(self, func_name):
        if func_name not in self.functions:
            raise ValueError(f"Error semántico: La función '{func_name}' no está declarada.")
        return self.functions[func_name]

    def add_variable_to_function(self, func_name, var_name, var_type):
        function_info = self.get_function(func_name)
        function_info["variable_table"].add_variable(var_name, var_type)

    def get_variable_type_in_function(self, func_name, var_name):
        function_info = self.get_function(func_name)
        return function_info["variable_table"].get_variable_type(var_name)