import argparse
from parser import Parser
from lexer import LexicalAnalyzer
from standardizer.ast_factory import ASTFactory
from cse_factory import CSEMachineFactory

def main():
    parser = argparse.ArgumentParser(description='Process some RPAL files.')
    parser.add_argument('file_name', type=str, help='The RPAL program input file')
    parser.add_argument('-ast', action='store_true', help='Print the abstract syntax tree')
    parser.add_argument('-sast', action='store_true', help='Print the standardized abstract syntax tree')

    args = parser.parse_args()

    with open(args.file_name, "r") as input_file:
        input_text = input_file.read()

    # Tokenize the input text
    lexer = LexicalAnalyzer(input_text)
    tokens = lexer.tokenize()

    try:
        parser = Parser(tokens)
        ast = parser.parse()
        if ast is None:
            return

        # Print AST if requested
        if args.ast:
            ast.print_ast()
            return
         # Abstract Syntax Tree (AST)
        string_ast = parser.convert_ast_to_string_ast()
        if args.ast:
            for string in string_ast:
                print(string)
            return
        # Standardized Abstract Syntax Tree (SAST)
        ast_factory = ASTFactory()
        ast = ast_factory.get_abstract_syntax_tree(string_ast)
        ast.standardize()
        if args.sast:
            ast.print_ast()
            return

        # Run CSE Machine
        cse_machine_factory = CSEMachineFactory()
        cse_machine = cse_machine_factory.get_cse_machine(ast)
        print("Output of the above program is:")
        print(cse_machine.get_answer())

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
