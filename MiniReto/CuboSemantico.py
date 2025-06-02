# Cubo Semántico

cubo_semantico = {
    # Operadores Aritméticos
    '+': {
        ('INT', 'INT'): 'INT',
        ('INT', 'FLOAT'): 'FLOAT',
        ('FLOAT', 'INT'): 'FLOAT',
        ('FLOAT', 'FLOAT'): 'FLOAT',
        ('STRING', 'STRING'): 'STRING'
    },
    '-': {
        ('INT', 'INT'): 'INT',
        ('INT', 'FLOAT'): 'FLOAT',
        ('FLOAT', 'INT'): 'FLOAT',
        ('FLOAT', 'FLOAT'): 'FLOAT'
    },
    '*': {
        ('INT', 'INT'): 'INT',
        ('INT', 'FLOAT'): 'FLOAT',
        ('FLOAT', 'INT'): 'FLOAT',
        ('FLOAT', 'FLOAT'): 'FLOAT'
    },
    '/': {
        ('INT', 'INT'): 'FLOAT',
        ('INT', 'FLOAT'): 'FLOAT',
        ('FLOAT', 'INT'): 'FLOAT',
        ('FLOAT', 'FLOAT'): 'FLOAT'
    },
    # Operadores Relacionales
    '<': {
        ('INT', 'INT'): 'BOOL',
        ('INT', 'FLOAT'): 'BOOL',
        ('FLOAT', 'INT'): 'BOOL',
        ('FLOAT', 'FLOAT'): 'BOOL'
    },
    '>': {
        ('INT', 'INT'): 'BOOL',
        ('INT', 'FLOAT'): 'BOOL',
        ('FLOAT', 'INT'): 'BOOL',
        ('FLOAT', 'FLOAT'): 'BOOL'
    },
    '!=': {
        ('INT', 'INT'): 'BOOL',
        ('INT', 'FLOAT'): 'BOOL', # Normalmente no tendría mucho sentido comparar float-int, pero lo permitiré para flexibilidad
        ('FLOAT', 'INT'): 'BOOL',
        ('FLOAT', 'FLOAT'): 'BOOL',
        ('STRING', 'STRING'): 'BOOL'
    },
    # Asignación
    '=': {
        ('INT', 'INT'): 'INT',
        ('FLOAT', 'FLOAT'): 'FLOAT',
        ('STRING', 'STRING'): 'STRING'
    }
}

# Función para consultar el cubo semántico
def check_semantic(operator, left_type, right_type):
    """
    Consulta el cubo semántico para validar operaciones.
    Lanza un error si la operación no es válida.
    """
    if operator not in cubo_semantico:
        raise ValueError(f"Operador '{operator}' no está definido en el cubo semántico.")

    result_type = cubo_semantico.get(operator, {}).get((left_type, right_type), None)
    if result_type is None:
        raise TypeError(
            f"Error semántico: No se puede aplicar '{operator}' entre '{left_type}' y '{right_type}'.\n"
            f"Tipos válidos para '{operator}': {list(cubo_semantico[operator].keys())}")
    return result_type
