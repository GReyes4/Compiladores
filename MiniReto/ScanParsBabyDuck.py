from lark import Lark, UnexpectedInput
import os
from CuboSemantico import check_semantic
from AnalizadorSemantico import SemanticAnalyzer

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

    except UnexpectedInput as e:
        print("Error de sintaxis:")
        print(e)

# Ejemplo de código fuente en BabyDuck
babyduck_code = """
PROGRAM Prueba5;
VAR x : INT;
y : FLOAT;
MAIN {
    x = (10 + 2) * 3 - 4 + 2;
    y = 5.0 + x * 2;
    IF (y < 20.5) {
        PRINT("y es menor");
    };
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
    parse_code(babyduck_code, GRAMMAR_FILE)