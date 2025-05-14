#!/usr/bin/env python3

import sys
from parser import parse_file
from standardizer import standardize_ast
from cse_machine import run_cse_machine

def main():
    """Main entry point for RPAL interpreter"""
    if len(sys.argv) < 2:
        print("Usage: python myrpal.py <filename> [-ast]")
        sys.exit(1)
    
    filename = sys.argv[1]
    print_ast = False
    
    if len(sys.argv) > 2 and sys.argv[2] == "-ast":
        print_ast = True
    
    # Parse input file to produce AST
    ast = parse_file(filename)
    
    if print_ast:
        # Only print the AST if -ast flag is provided
        ast.print_ast()
        return
    
    # Standardize AST to ST
    st = standardize_ast(ast)
    
    # Execute ST with CSE machine
    run_cse_machine(st)

if __name__ == "__main__":
    main()