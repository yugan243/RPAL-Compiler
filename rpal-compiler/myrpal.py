import sys
from parser import parse_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 myrpal.py [-ast] file_name")
        sys.exit(1)

    ast_switch = sys.argv[1] == '-ast'
    file_name = sys.argv[2] if ast_switch else sys.argv[1]

    ast = parse_file(file_name)

    if ast_switch:
        ast.print_ast()
    else:
        # Placeholder for ST conversion and CSE machine
        print("Evaluation not implemented")

if __name__ == "__main__":
    main()