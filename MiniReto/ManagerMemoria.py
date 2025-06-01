class VirtualMemoryManager:
    def __init__(self):
        self.counters = {
            'global': {'INT': 1000, 'FLOAT': 2000, 'STRING': 3000, 'BOOL': 4000},
            'local': {'INT': 5000, 'FLOAT': 6000, 'STRING': 7000, 'BOOL': 8000},
            'temp': {'INT': 9000, 'FLOAT': 10000, 'STRING': 11000, 'BOOL': 12000},
            'const': {'INT': 13000, 'FLOAT': 14000, 'STRING': 15000, 'BOOL': 16000}
        }
        self.constants_table = {}

    def get_address(self, scope, var_type):
        addr = self.counters[scope][var_type]
        self.counters[scope][var_type] += 1
        return addr

    def get_const_address(self, value, var_type):
        if value in self.constants_table:
            return self.constants_table[value]
        addr = self.get_address('const', var_type)
        self.constants_table[value] = addr
        return addr