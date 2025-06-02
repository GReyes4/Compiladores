from lark import Lark, UnexpectedInput
import os
from CuboSemantico import check_semantic
from AnalizadorSemantico import SemanticAnalyzer
from MaquinaVirtual import BabyDuckVM
from MemoriaEjecucion import ExecutionMemory

# Obtener la ruta del directorio donde está el script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ruta al archivo de gramática (esta relativa al script)
GRAMMAR_FILE = os.path.join(BASE_DIR, "grammar.lark")

def load_grammar(grammar_file):
    """Carga de la gramática"""

    if not os.path.exists(grammar_file):
        raise FileNotFoundError(f"No se encontró el archivo de gramática: {grammar_file}")
    
    with open(grammar_file, "r", encoding="utf-8") as file:
        grammar = file.read()
    
    return grammar 

def parse_code(code, grammar_file):
    """Parseo del código fuente con la gramática"""
    # Cargar gramática
    grammar = load_grammar(grammar_file)
    
    # Crear el parser
    parser = Lark(grammar, start='start', parser='lalr')
    
    try:
        # Parsear el código fuente
        tree = parser.parse(code)
        #print("Árbol sintáctico generado:")
        #print(tree.pretty())

        # Realizar el análisis semántico
        analyzer = SemanticAnalyzer()
        analyzer.analyze(tree)
        print("Análisis semántico completado sin errores.")
        return analyzer
        
    except UnexpectedInput as e:
        print("Error de sintaxis:")
        print(e)

# Ejemplo de código fuente en BabyDuck
babyduck_code = """
PROGRAM FibonacciFunc;
VAR n : INT;
VOID fibonacci(num : INT) [ VAR a, b, c, i : INT; {
    a = 0;
    b = 1;
    PRINT(a);
    PRINT(b);
    i = 2;
    WHILE (i < num) DO {
        c = a + b;
        PRINT(c);
        a = b;
        b = c;
        i = i + 1;
    };
} ];
MAIN {
    n = 12;
    fibonacci(n);
}
END
"""


# Prueba del cubo semántico
def test_cubo_semantico():
    assert check_semantic('+', 'INT', 'INT') == 'INT'
    assert check_semantic('*', 'FLOAT', 'INT') == 'FLOAT'
    try:
        check_semantic('+', 'STRING', 'INT')
    except TypeError as e:
        assert "Error semántico" in str(e)

# Procesar código
if __name__ == "__main__":
    analyzer = parse_code(babyduck_code, GRAMMAR_FILE)

    if analyzer:
        quadruples = analyzer.quad_gen.quad_queue
        # Inicializa la memoria global (puedes llenarla con valores iniciales si lo deseas)
        global_memory = ExecutionMemory()

        # Inicializa las constantes en la memoria global
        for const_value, address in analyzer.memory.constants_table.items():
            # Convierte el valor si es necesario (por ejemplo, de string a int/float)
            if isinstance(const_value, str) and const_value.isdigit():
                value = int(const_value)
            else:
                try:
                    value = float(const_value)
                except (ValueError, TypeError):
                    value = const_value
            global_memory.set_value(address, value)
        
        # Ejecuta la máquina virtual
        print("\nEjecutando el programa...")
        vm = BabyDuckVM(quadruples, global_memory, start_ip=analyzer.main_start_quad)
        vm.run()

