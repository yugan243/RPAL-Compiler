import sys
from lexer import Lexer
from parser import Parser
from standardizer import Standardizer
from cse_machine import CSEMachine

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 myrpal.py [-ast] file_name")
        return

    ast_switch = sys.argv[1] == '-ast'
    file_name = sys.argv[2] if ast_switch else sys.argv[1]

    with open(file_name, 'r') as f:
        input_text = f.read()

    # Lexical Analysis
    lexer = Lexer(input_text)
    tokens = lexer.tokenize()

    # Parsing
    parser = Parser(tokens)
    ast = parser.parse()

    if ast_switch:
        parser.print_ast(ast)
        return

    # Standardize
    standardizer = Standardizer()
    st = standardizer.standardize(ast)

    # Evaluate
    cse = CSEMachine(st)
    result = cse.evaluate()
    print(result)

if __name__ == "__main__":
    main()