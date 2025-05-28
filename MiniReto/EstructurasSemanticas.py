# Estructuras semánticas de Tabla de Variables y Directorio de Funciones

class VariableInfo:
    def __init__(self, name, var_type, scope='local'):
        self.name = name
        self.type = var_type
        self.scope = scope  # 'global' o 'local'

    def __repr__(self):
        return f"VariableInfo(name={self.name}, type={self.type}, scope={self.scope})"

class TablaVariables:
    def __init__(self):
        self.variables = {}

    def add_variable(self, name, var_type, scope='local'):
        if name in self.variables:
            raise ValueError(f"Variable '{name}' ya declarada en este ámbito.")
        self.variables[name] = VariableInfo(name, var_type, scope)

    def get_variable(self, name):
        return self.variables.get(name)

    def __repr__(self):
        return f"TablaVariables({self.variables})"

class FuncionInfo:
    def __init__(self, name, return_type, param_types):
        self.name = name
        self.return_type = return_type
        self.param_types = param_types  # lista de tipos de parámetros
        self.tabla_variables = TablaVariables()

    def __repr__(self):
        return (f"FuncionInfo(name={self.name}, return_type={self.return_type}, "
                f"param_types={self.param_types}, tabla_variables={self.tabla_variables})")

class DirectorioFunciones:
    def __init__(self):
        self.funciones = {}
        self.global_vars = TablaVariables()

    def add_funcion(self, name, return_type, param_types):
        if name in self.funciones:
            raise ValueError(f"Función '{name}' ya declarada.")
        self.funciones[name] = FuncionInfo(name, return_type, param_types)

    def get_funcion(self, name):
        return self.funciones.get(name)

    def add_global_variable(self, name, var_type):
        self.global_vars.add_variable(name, var_type, scope='global')
        print(f"Variable global '{name}' de tipo '{var_type}' añadida.")

    def get_global_variable(self, name):
        return self.global_vars.get_variable(name)

    def __repr__(self):
        return (f"DirectorioFunciones(funciones={self.funciones}, "
                f"global_vars={self.global_vars})")