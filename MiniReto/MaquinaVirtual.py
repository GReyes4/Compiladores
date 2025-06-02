from MemoriaEjecucion import ExecutionMemory

class BabyDuckVM:
    def __init__(self, quadruples, memory, start_ip=0):
        self.quadruples = quadruples
        self.global_memory = memory  # Solo para globales y constantes
        self.local_stack = []  # Pila de contextos locales/temporales
        self.current_local = ExecutionMemory()
        self.pending_local = None  # Contexto preparado por ERA
        self.ip = start_ip # Instruction pointer
        self.call_stack = []  # Para GOSUB/ERA
        self.param_stack = []  # Para pasar parámetros

    def get_value(self, address):
        # Determina si es global/constante o local/temporal
        if 1000 <= address < 5000 or 13000 <= address < 17000:
            return self.global_memory.get_value(address)
        else:
            return self.current_local.get_value(address)
        
    def set_value(self, address, value):
        if 1000 <= address < 5000 or 13000 <= address < 17000:
            self.global_memory.set_value(address, value)
        else:
            self.current_local.set_value(address, value)
        

    def run(self):
        while self.ip < len(self.quadruples):
            quad = self.quadruples[self.ip]
            op, left, right, res = quad

            if op == '=':
                value = self.get_value(left)
                self.set_value(res, value)
            elif op == '+':
                l = self.get_value(left)
                r = self.get_value(right)
                self.set_value(res, l + r)
            elif op == '-':
                l = self.get_value(left)
                r = self.get_value(right)
                self.set_value(res, l - r)
            elif op == '*':
                l = self.get_value(left)
                r = self.get_value(right)
                self.set_value(res, l * r)
            elif op == '/':
                l = self.get_value(left)
                r = self.get_value(right)
                self.set_value(res, l / r)
            elif op == '<':
                l = self.get_value(left)
                r = self.get_value(right)
                self.set_value(res, l < r)
            elif op == '>':
                l = self.get_value(left)
                r = self.get_value(right)
                self.set_value(res, l > r)
            elif op == '!=':
                l = self.get_value(left)
                r = self.get_value(right)
                self.set_value(res, l != r)
            elif op == 'PRINT':
                # Si es una dirección virtual, imprime el valor; si es string literal, imprime directo
                if isinstance(left, int):
                    print(self.get_value(left))
                else:
                    print(left)
            elif op == 'ERA':
                # Prepara el activation record
                self.pending_local = ExecutionMemory()
                self.param_stack = []
            elif op == 'PARAM':
                # PARAM <valor>, -, <dir_param>
                self.param_stack.append((res, left))
            elif op == 'GOSUB':
                # GOSUB <func_name>, -, <quad_inicio>
                # Guarda el contexto actual y el ip de retorno
                self.local_stack.append(self.current_local)
                self.call_stack.append(self.ip + 1)
                # Activa el contexto preparado
                self.current_local = self.pending_local
                # Asigna parámetros a direcciones virtuales locales
                for param_addr, value_addr in self.param_stack:
                    value = self.get_value(value_addr)
                    self.current_local.set_value(param_addr, value)
                self.param_stack = []
                self.ip = res
                continue
            elif op == 'ENDPROC':
                # Restaura el contexto anterior y el ip de retorno
                self.current_local = self.local_stack.pop()
                self.ip = self.call_stack.pop()
                continue
            elif op == 'GOTO':
                self.ip = res
                continue
            elif op == 'GOTOF':
                cond = self.get_value(left)
                if not cond:
                    self.ip = res
                    continue
            self.ip += 1