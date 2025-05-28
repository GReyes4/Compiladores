# Analizador semántico
from lark import Tree, Token
from EstructurasSemanticas import FunctionDirectory  # Importa las estructuras de datos
from CuboSemantico import check_semantic          # Importa el cubo semántico
from RepresentacionCuadruplos import QuadrupleGenerator # Importa el generador de cuádruplos

# Mapeo de tokens a operadores
token_to_operator = {
    "PLUS": "+",
    "MINUS": "-",
    "MULT": "*",
    "DIV": "/",
    "LT": "<",
    "GT": ">",
    "NEQ": "!=",
    "ASSIGN": "="
}

class SemanticAnalyzer:
    def __init__(self):
        self.func_dir = FunctionDirectory()
        self.current_function = None  # Para rastrear la función actual
        self.current_type = None  # Para rastrear el tipo actual en declaraciones

    def traverse_tree(self, tree):
        if isinstance(tree, Tree):
            if tree.data == "programa":
                self._process_programa(tree)
            elif tree.data == "vars":
                self._process_vars(tree)
            elif tree.data == "var_plus":
                self._process_var_plus(tree)
            elif tree.data == "funcs":
                self._process_funcs(tree)
            elif tree.data == "body":
                self._process_body(tree)
            elif tree.data == "statement":
                self._process_statement(tree)
            elif tree.data == "asignacion":
                self._process_asignacion(tree)
            elif tree.data == "condition":
                self._process_condition(tree)
            elif tree.data == "print":
                self._process_print(tree)
            elif tree.data == "expression":
                return self._process_expression(tree)
            else:
                for child in tree.children:
                    self.traverse_tree(child)
        elif isinstance(tree, Token):
            pass  # Los tokens son hojas y no necesitan procesamiento adicional

    def _process_programa(self, tree):
        # Procesar declaración del programa
        program_id = tree.children[1].value
        self.func_dir.add_function(program_id, "PROGRAM")
        self.current_function = program_id
        for child in tree.children[3:]:
            self.traverse_tree(child)

    def _process_vars(self, tree):
        print("Procesando vars:", tree)
        # Procesar declaración inicial de variables
        if len(tree.children) > 1:  # Verificar si hay declaraciones
            self._process_var_declaration(tree)
        
        # Procesar vars_plus recursivamente
        if len(tree.children) > 5 and isinstance(tree.children[5], Tree) and tree.children[5].data == "var_plus":
            #print("Encontrado var_plus:", tree.children[5])
            self._process_var_plus(tree.children[5])

    def _process_var_declaration(self, tree):
        # Extraer IDs y tipo
        ids = self._extract_ids(tree.children[1])  # Lista de IDs
        type_node = tree.children[3]
        if isinstance(type_node, Tree):
            var_type = type_node.children[0].type
        else:
            var_type = type_node.type
        
        # Agregar variables al directorio de funciones
        for var_id in ids:
            self.func_dir.add_variable_to_function(self.current_function, var_id, var_type)

    def _process_var_plus(self, tree):
        # Si el nodo está vacío, termina la recursión
        if not tree.children:
            return
        # Procesar declaración de variable en var_plus
        self._process_var_declaration(tree)
        # Si hay más declaraciones, procesarlas recursivamente
        if len(tree.children) > 4 and isinstance(tree.children[4], Tree) and tree.children[4].data == "var_plus":
            self._process_var_plus(tree.children[4])

    def _extract_ids(self, ids_node):
        # Extraer lista de IDs desde un nodo 'ids'
        ids = []
        while ids_node:
            if isinstance(ids_node, Tree) and ids_node.data == "ids":
                ids.append(ids_node.children[0].value)
                ids_node = ids_node.children[1]  # Avanzar al siguiente ID si hay coma
            else:
                break
        return ids

    def _process_funcs(self, tree):
        # Procesar declaración de funciones
        if not tree.children:
            return
        func_type = tree.children[0].type
        func_id = tree.children[1].value
        self.func_dir.add_function(func_id, func_type)
        self.current_function = func_id
        # Procesar vars dentro de la función
        self.traverse_tree(tree.children[5])
        # Procesar body de la función
        self.traverse_tree(tree.children[6])
        # Procesar funciones adicionales recursivamente
        if len(tree.children) > 8:
            self.traverse_tree(tree.children[8])

    def _process_body(self, tree):
        # Procesar cuerpo de una función o bloque
        for child in tree.children[1:-1]:  # Ignorar LBRACE y RBRACE
            self.traverse_tree(child)

    def _process_statement(self, tree):
        # Procesar instrucciones dentro de un bloque
        for child in tree.children:
            self.traverse_tree(child)

    def _process_asignacion(self, tree):
        var_id = tree.children[0].value
        var_type = self.func_dir.get_variable_type_in_function(self.current_function, var_id)
        
        # Verificar si hay una expresión
        if len(tree.children) > 2:
            expr_type = self.traverse_tree(tree.children[2])
            result_type = check_semantic("=", var_type, expr_type)
            if result_type != var_type:
                raise ValueError(f"Error semántico: No se puede asignar un valor de tipo '{expr_type}' a la variable '{var_id}' de tipo '{var_type}'.")
        else:
            raise ValueError(f"Error semántico: Falta una expresión en la asignación de la variable '{var_id}'.")

    def _process_condition(self, tree):
        # Procesar condición
        if len(tree.children) > 2:
            condition_expr = self.traverse_tree(tree.children[2])
            if condition_expr != "BOOL":
                raise ValueError(f"Error semántico: La expresión de la condición debe ser de tipo 'BOOL', pero es '{condition_expr}'.")
        else:
            raise ValueError("Error semántico: Falta una expresión en la condición.")
        
        # Procesar cuerpo de la condición
        self.traverse_tree(tree.children[4])
        
        # Procesar else si existe
        if len(tree.children) > 6:
            self.traverse_tree(tree.children[6])

    def _process_print(self, tree):
        # Procesar impresión
        print_content = tree.children[2]
        self.traverse_tree(print_content)
    
    def _process_expression(self, tree):
        # Procesar el primer término (exp)
        exp_type = self._process_exp(tree.children[0])  # Tipo del primer término
        
        # Verificar si hay un operador opcional (exp_opc)
        if len(tree.children) > 1 and tree.children[1].children:
            operator_token = tree.children[1].children[0].type  # Operador (LT, GT, NEQ, etc.)
            operator = token_to_operator.get(operator_token)
            right_type = self._process_exp(tree.children[1].children[1])  # Tipo del segundo término
            
            # Validar la operación usando el cubo semántico
            return check_semantic(operator, exp_type, right_type)
        
        # Si no hay operador, devolver el tipo del primer término
        return exp_type
    
    def _process_exp(self, tree):
        # Procesar el primer término (termino)
        term_type = self._process_termino(tree.children[0])  # Tipo del término
        
        # Verificar si hay un operador opcional (signo)
        if len(tree.children) > 1 and isinstance(tree.children[1], Tree) and tree.children[1].children:
            operator_token = tree.children[1].children[0].type  # Token del operador (PLUS, MINUS)
            operator = token_to_operator.get(operator_token)  # Mapear a operador del cubo semántico
            if operator is None:
                raise ValueError(f"Operador '{operator_token}' no está definido en el cubo semántico.")
            
            right_type = self._process_exp(tree.children[1].children[1])  # Tipo del segundo término
            
            # Validar la operación usando el cubo semántico
            return check_semantic(operator, term_type, right_type)
        
        # Si no hay operador, devolver el tipo del término
        return term_type
    
    def _process_termino(self, tree):
        # Procesar el primer factor
        factor_type = self._process_factor(tree.children[0])  # Tipo del factor
        
        # Verificar si hay un operador opcional (muldiv)
        if len(tree.children) > 1 and isinstance(tree.children[1], Tree) and tree.children[1].children:
            operator_token = tree.children[1].children[0].type  # Token del operador (MULT, DIV)
            operator = token_to_operator.get(operator_token)  # Mapear a operador del cubo semántico
            if operator is None:
                raise ValueError(f"Operador '{operator_token}' no está definido en el cubo semántico.")
            
            right_type = self._process_termino(tree.children[1].children[1])  # Tipo del segundo término
            
            # Validar la operación usando el cubo semántico
            return check_semantic(operator, factor_type, right_type)
        
        # Si no hay operador, devolver el tipo del factor
        return factor_type
    
    def _process_factor(self, tree):
        # Procesar fact_signo (opcional)
        fact_signo = tree.children[0]
        if isinstance(fact_signo, Tree) and fact_signo.data == "fact_signo" and fact_signo.children:
            # Si hay un signo (+ o -), ignorarlo ya que no afecta el tipo
            pass

        # Procesar ct_id
        ct_id_node = tree.children[1]
        if isinstance(ct_id_node, Tree) and ct_id_node.data == "ct_id":
            # Caso 1: cte (constante)
            if len(ct_id_node.children) > 0 and isinstance(ct_id_node.children[0], Tree) and ct_id_node.children[0].data == "cte":
                cte_token = ct_id_node.children[0].children[0]
                if cte_token.type == "CTE_INT":
                    return "INT"
                elif cte_token.type == "CTE_FLOAT":
                    return "FLOAT"
            
            # Caso 2: ID (variable)
            elif len(ct_id_node.children) > 0 and isinstance(ct_id_node.children[0], Token) and ct_id_node.children[0].type == "ID":
                var_id = ct_id_node.children[0].value
                return self.func_dir.get_variable_type_in_function(self.current_function, var_id)

        # Si no se encuentra un tipo válido, lanzar un error
        raise ValueError(f"Error semántico: No se pudo determinar el tipo del factor en {tree}.")




