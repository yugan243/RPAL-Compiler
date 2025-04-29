# RPAL Compiler

## Project Description

This project is a **compiler** for the **RPAL** (Recursive Procedural Algorithmic Language). The goal is to implement a **lexical analyzer** and a **parser** for RPAL programs, generating an **Abstract Syntax Tree (AST)** as output. Further steps will involve converting the AST to a **Standardized Tree (ST)** and implementing a **CSE machine** to evaluate RPAL programs.

## Features

- **Lexical Analyzer**: Tokenizes the RPAL program.
- **Parser**: Generates the Abstract Syntax Tree (AST).
- **AST to ST Conversion**: Converts the AST to a standardized tree.
- **CSE Machine**: Executes the RPAL program based on the ST.

## Setup Instructions

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/RPAL-Compiler.git
    ```

2. Navigate to the project directory:
    ```bash
    cd RPAL-Compiler
    ```

3. Run the RPAL compiler:
    ```bash
    python myrpal.py your_program.rpal
    ```

## Project Structure

- **`myrpal.py`**: The main entry point for running the RPAL compiler.
- **`lexer.py`**: Contains the lexical analysis code.
- **`parser.py`**: Contains the code to parse the tokens and generate the AST.
- **`ast.py`**: Contains the representation and methods related to the Abstract Syntax Tree.
- **`standardizer.py`**: Converts the AST to the Standardized Tree (ST).
- **`cse_machine.py`**: Implements the CSE machine to execute RPAL code.
- **`utils.py`**: Contains helper functions used throughout the project.
- **`tests/`**: Directory containing sample RPAL programs for testing.
- **`docs/`**: Documentation and reports related to the project.

## Contributing

This is a course project for the Programming Languages module, developed by Yugan Nimsara and Pubudu Manoj. Only authorized collaborators are allowed to contribute to this repository. Please follow the code structure and guidelines defined in this project.

## License

This project is licensed under the **Apache 2.0 License** - see the [LICENSE](LICENSE) file for details.
