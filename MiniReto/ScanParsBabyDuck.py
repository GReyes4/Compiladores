from lark import Lark, UnexpectedInput
import os

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
        print("Árbol sintáctico generado:")
        print(tree.pretty())
    except UnexpectedInput as e:
        print("Error de sintaxis:")
        print(e)

# Ejemplo de código fuente en BabyDuck
babyduck_code = """
PROGRAM Test;
VAR x : INT;
MAIN {
    x = 10;
    PRINT("Hola Mundo");
}
END
"""

# Procesar código
if __name__ == "__main__":
    parse_code(babyduck_code, GRAMMAR_FILE)