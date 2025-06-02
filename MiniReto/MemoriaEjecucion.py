class ExecutionMemory:
    def __init__(self):
        self.memory = {}  # {direccion_virtual: valor}

    def set_value(self, address, value):
        self.memory[address] = value

    def get_value(self, address):
        return self.memory.get(address, None)