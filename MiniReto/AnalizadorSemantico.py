from lark import Visitor, Token, Tree
from CuboSemantico import check_semantic
from EstructurasSemanticas import DirectorioFunciones
from RepresentacionCuadruplos import QuadrupleGenerator

class SemanticAnalyzer(Visitor):
    def __init__(self):
        self.dir_func = DirectorioFunciones()
        self.current_func = None  # None = global scope
        self.quad_gen = QuadrupleGenerator()

    def analyze(self, tree):
        self.programa(tree.children[0])
        print("Directorio de Funciones construido:")
        print(self.dir_func)
        self.quad_gen.print_quadruples()

    def _find_variable(self, name):
        if self.current_func:
            var = self.current_func.tabla_variables.get_variable(name)
            if var:
                return var
        return self.dir_func.get_global_variable(name)

    # --- Programa principal ---
    def programa(self, tree):
        # children: [PROGRAM, ID, SEMICOLON, vars, funcs, MAIN, body, END]
        # Visitar primero las declaraciones de variables y funciones
        self.visit(tree.children[3])  # vars
        funcs_node = tree.children[4]
        # Procesa todas las funciones manualmente
        while len(funcs_node.children) > 0:
            self.funcs(funcs_node)
            # El siguiente funcs está en la posición 10
            funcs_node = funcs_node.children[10] if len(funcs_node.children) > 10 else Tree('funcs', [])
        self.visit(tree.children[6])  # body

    # --- Variables ---
    def vars(self, tree):
        if len(tree.children) == 0:
            return
        var_type = tree.children[3].children[0].value
        ids = self._collect_ids(tree.children[1])
        #print("Añadiendo vars, con .current_func:", self.current_func)
        if self.current_func:
            for var in ids:
                self.current_func.tabla_variables.add_variable(var, var_type)
                print(f"Variable local '{var}' de tipo '{var_type}' añadida.")
        else:
            for var in ids:
                self.dir_func.add_global_variable(var, var_type)
        var_plus_node = tree.children[5]
        while isinstance(var_plus_node, Tree) and var_plus_node.data == 'var_plus' and len(var_plus_node.children) > 0:
            var_type = var_plus_node.children[2].children[0].value
            ids = self._collect_ids(var_plus_node.children[0])
            if self.current_func:
                for var in ids:
                    self.current_func.tabla_variables.add_variable(var, var_type)
                    print(f"Variable local '{var}' de tipo '{var_type}' añadida.")
            else:
                for var in ids:
                    self.dir_func.add_global_variable(var, var_type)
            var_plus_node = var_plus_node.children[4] if len(var_plus_node.children) > 4 else None

    def var_plus(self, tree):
        return

    # --- Declaración de funciones ---
    def funcs(self, tree):
        if len(tree.children) == 0: # Por si no hay funciones
            return
        # children: [VOID, ID, LPAREN, funcs_param, RPAREN, LBRACKET, vars, body, RBRACKET, SEMICOLON, funcs]
        func_name = tree.children[1].value
        param_types, param_names = self._collect_params(tree.children[3])
        self.dir_func.add_funcion(func_name, 'VOID', param_types)
        self.current_func = self.dir_func.get_funcion(func_name)
        # Agregar parámetros como variables locales
        for name, typ in zip(param_names, param_types):
            self.current_func.tabla_variables.add_variable(name, typ)
        # Las variables locales se agregan en vars()
        # --- VISITA LAS VARIABLES LOCALES ANTES DEL BODY ---
        self.visit(tree.children[6])  # vars
        # Ahora sí, analiza el cuerpo
        self.visit(tree.children[7])  # body
        self.current_func = None  # Reset al terminar
        # Procesa posibles funciones siguientes
        self.visit(tree.children[10])  # funcs

    def funcs_param(self, tree):
        # children: [ID, COLON, type, funcs_com]
        if len(tree.children) == 0:
            return ([], [])
        param_name = tree.children[0].value
        param_type = tree.children[2].children[0].value
        params = [(param_name, param_type)]
        params += self._collect_params(tree.children[3])
        if not params:
            return ([], [])
        # Solo incluye tuplas válidas (de dos elementos)
        filtered_params = [p for p in params if isinstance(p, tuple) and len(p) == 2]
        return ([typ for _, typ in filtered_params], [name for name, _ in filtered_params])

    def funcs_com(self, tree):
        if len(tree.children) == 0:
            return []
        return self._collect_params(tree.children[1])

    # --- Utilidades ---
    def _collect_ids(self, ids_tree):
        # ids: ID com
        ids = [ids_tree.children[0].value]
        ids += self._collect_com(ids_tree.children[1])
        return ids

    def _collect_com(self, com_tree):
        # com: COMMA ids | 
        if len(com_tree.children) == 0:
            return []
        return self._collect_ids(com_tree.children[1])

    def _collect_params(self, param_tree):
        if not hasattr(param_tree, 'children') or len(param_tree.children) == 0:
            return ([], [])
        if hasattr(param_tree, 'data') and param_tree.data == 'funcs_param':
            param_name = param_tree.children[0].value
            param_type = param_tree.children[2].children[0].value
            params = [(param_name, param_type)]
            params_types, params_names = self._collect_params(param_tree.children[3])
            return ([param_type] + params_types, [param_name] + params_names)
        elif hasattr(param_tree, 'data') and param_tree.data == 'funcs_com':
            if len(param_tree.children) == 0:
                return ([], [])
            return self._collect_params(param_tree.children[1])
        else:
            return ([], [])
        
    def asignacion(self, tree):
        var_name = tree.children[0].value
        var_info = self._find_variable(var_name)
        if not var_info:
            raise Exception(f"Variable '{var_name}' no declarada.")
        expr_type = self._get_expression_type(tree.children[2])
        try:
            check_semantic('=', var_info.type, expr_type)
        except Exception as e:
            raise Exception(f"Error de tipo en asignación a '{var_name}': {e}")
        expr_result = self._generate_expression_quadruples(tree.children[2])
        self.quad_gen.add_quadruple('=', expr_type, '-', var_name)
        
    def _get_expression_type(self, tree):
        # expression: exp exp_opc
        if tree.data == 'expression':
            left_type = self._get_expression_type(tree.children[0])
            if len(tree.children) > 1 and tree.children[1].children:
                op_node = tree.children[1].children[0]
                if isinstance(op_node, Token):
                    op_type = op_node.type
                else:
                    op_type = op_node.data
                right_type = self._get_expression_type(tree.children[1].children[1])
                op_map = {'LT': '<', 'GT': '>', 'NEQ': '!='}
                op_str = op_map.get(op_type, op_type)
                return check_semantic(op_str, left_type, right_type)
            return left_type
        # exp: termino signo
        elif tree.data == 'exp':
            left_type = self._get_expression_type(tree.children[0])
            if len(tree.children) > 1 and tree.children[1].children:
                op_node = tree.children[1].children[0]
                if isinstance(op_node, Token):
                    op_type = op_node.type
                else:
                    op_type = op_node.data
                right_type = self._get_expression_type(tree.children[1].children[1])
                op_map = {'PLUS': '+', 'MINUS': '-'}
                op_str = op_map.get(op_type, op_type)
                return check_semantic(op_str, left_type, right_type)
            return left_type
        # termino: factor muldiv
        elif tree.data == 'termino':
            left_type = self._get_expression_type(tree.children[0])
            if len(tree.children) > 1 and tree.children[1].children:
                op_node = tree.children[1].children[0]
                if isinstance(op_node, Token):
                    op_type = op_node.type
                else:
                    op_type = op_node.data
                right_type = self._get_expression_type(tree.children[1].children[1])
                op_map = {'MULT': '*', 'DIV': '/'}
                op_str = op_map.get(op_type, op_type)
                return check_semantic(op_str, left_type, right_type)
            return left_type
        # factor: LPAREN expression RPAREN | fact_signo ct_id | ct_id
        elif tree.data == 'factor':
            first = tree.children[0]
            if isinstance(first, Tree) and first.data == 'fact_signo':
                # Unario, solo propagamos el tipo
                return self._get_expression_type(tree.children[1])
            elif isinstance(first, Token) and first.type == 'LPAREN':
                return self._get_expression_type(tree.children[1])
            else:
                return self._get_expression_type(first)
        # ct_id: ID | cte
        elif tree.data == 'ct_id':
            first = tree.children[0]
            if isinstance(first, Token) and first.type == 'ID':
                var_name = first.value
                var_info = self._find_variable(var_name)
                if not var_info:
                    raise Exception(f"Variable '{var_name}' no declarada.")
                return var_info.type
            else:
                return self._get_expression_type(first)
        # cte: CTE_INT | CTE_FLOAT
        elif tree.data == 'cte':
            token = tree.children[0]
            if token.type == 'CTE_INT':
                return 'INT'
            elif token.type == 'CTE_FLOAT':
                return 'FLOAT'
        # STRING literal
        elif tree.data == 'print_cont' and isinstance(tree.children[0], Token) and tree.children[0].type == 'STRING':
            return 'STRING'
        raise Exception(f"No se pudo determinar el tipo de la expresión: {tree.data}")
    
    def _generate_expression_quadruples(self, tree):
        # Recorrido postorden para generar cuádruplos de expresiones
        if tree.data == 'expression':
            left = self._generate_expression_quadruples(tree.children[0])
            if len(tree.children) > 1 and tree.children[1].children:
                op_token = tree.children[1].children[0]
                op_map = {'LT': '<', 'GT': '>', 'NEQ': '!='}
                op = op_map.get(op_token.type, op_token.type)
                right = self._generate_expression_quadruples(tree.children[1].children[1])
                temp = self.quad_gen.generate_temp()
                self.quad_gen.add_quadruple(op, left, right, temp)
                return temp
            return left
        elif tree.data == 'exp':
            left = self._generate_expression_quadruples(tree.children[0])
            if len(tree.children) > 1 and tree.children[1].children:
                op_token = tree.children[1].children[0]
                op_map = {'PLUS': '+', 'MINUS': '-'}
                op = op_map.get(op_token.type, op_token.type)
                right = self._generate_expression_quadruples(tree.children[1].children[1])
                temp = self.quad_gen.generate_temp()
                self.quad_gen.add_quadruple(op, left, right, temp)
                return temp
            return left
        elif tree.data == 'termino':
            left = self._generate_expression_quadruples(tree.children[0])
            if len(tree.children) > 1 and tree.children[1].children:
                op_token = tree.children[1].children[0]
                op_map = {'MULT': '*', 'DIV': '/'}
                op = op_map.get(op_token.type, op_token.type)
                right = self._generate_expression_quadruples(tree.children[1].children[1])
                temp = self.quad_gen.generate_temp()
                self.quad_gen.add_quadruple(op, left, right, temp)
                return temp
            return left
        elif tree.data == 'factor':
            first = tree.children[0]
            if isinstance(first, Tree) and first.data == 'fact_signo':
                # Unario, solo propagamos el valor
                return self._generate_expression_quadruples(tree.children[1])
            elif isinstance(first, Token) and first.type == 'LPAREN':
                return self._generate_expression_quadruples(tree.children[1])
            else:
                return self._generate_expression_quadruples(first)
        elif tree.data == 'ct_id':
            first = tree.children[0]
            if isinstance(first, Token) and first.type == 'ID':
                return first.value
            else:
                return self._generate_expression_quadruples(first)
        elif tree.data == 'cte':
            token = tree.children[0]
            return token.value
        else:
            raise Exception(f"No se puede generar cuádruplo para: {tree.data}")
    
    def print(self, tree):
        # print: PRINT LPAREN print_cont RPAREN SEMICOLON
        print_cont_node = tree.children[2]
        self._handle_print_cont(print_cont_node)

    def _handle_print_cont(self, tree):
        # print_cont: expression print_com | STRING print_com
        if isinstance(tree.children[0], Token) and tree.children[0].type == 'STRING':
            value = tree.children[0].value
            self.quad_gen.add_quadruple('PRINT', value, '-', '-')
            # Si hay más, procesa recursivamente
            if len(tree.children) > 1 and len(tree.children[1].children) > 0:
                self._handle_print_cont(tree.children[1].children[1])
        else:
            # Es una expresión
            expr_result = self._generate_expression_quadruples(tree.children[0])
            self.quad_gen.add_quadruple('PRINT', expr_result, '-', '-')
            # Si hay más, procesa recursivamente
            if len(tree.children) > 1 and len(tree.children[1].children) > 0:
                self._handle_print_cont(tree.children[1].children[1])
