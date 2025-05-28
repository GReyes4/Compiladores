class QuadrupleGenerator:
    def __init__(self):
        self.operator_stack = []  # Pila de operadores
        self.operand_stack = []  # Pila de operandos
        self.type_stack = []     # Pila de tipos
        self.quad_queue = []     # Fila de cuádruplos
        self.temp_counter = 1    # Contador de temporales

    def generate_temp(self):
        """Genera un nombre único para una variable temporal."""
        temp_name = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp_name

    def add_quadruple(self, op, arg1, arg2, result):
        """Agrega un cuádruplo a la fila."""
        self.quad_queue.append((op, arg1, arg2, result))

    def print_quadruples(self):
        """Imprime todos los cuádruplos generados."""
        print("Cuádruplos generados:")
        for i, quad in enumerate(self.quad_queue, start=1):
            print(f"{i}: {quad}")



            