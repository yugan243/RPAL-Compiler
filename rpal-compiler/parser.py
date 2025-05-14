from lexer import tokenize_file

class ASTNode:
    def __init__(self,type,value = None):
        self.type = type
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        return child

    def print_ast(self, prefix=""):
        """Print AST in required format"""
        if self.value is not None:
            print(f"{prefix}{self.type}:{self.value}")
        else:
            print(f"{prefix}{self.type}")
        
        for child in self.children:
            child.print_ast(prefix + ".")
    
    def __str__(self):
        if self.value is not None:
            return f"{self.type}:{self.value}"
        return self.type

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[0]
    
    def error(self, expected=None):
        token = self.current_token
        if expected:
            raise Exception(f"Expected {expected}, got {token} at line {token.line}, column {token.column}")
        else:
            raise Exception(f"Unexpected token {token} at line {token.line}, column {token.column}")
    
    def consume(self, expected_type=None):
        #Consume the current token and advance to the next one
        if expected_type and self.current_token.type != expected_type:
            self.error(expected_type)
        
        if self.current_token_index < len(self.tokens) - 1:
            self.current_token_index += 1
            self.current_token = self.tokens[self.current_token_index]
        else:
            self.current_token = None
    
    def parse_e(self):
        if self.current_token.type == 'let':
            node = ASTNode('let')
            self.consume('let')
            node.add_child(self.parse_d())
            if self.current_token.type != 'in':
                self.error('in')
            self.consume('in')
            node.add_child(self.parse_e())
            return node
    
        elif self.current_token.type == 'fn':
           
            node = ASTNode('lambda')
            self.consume('fn')
            # Parse one or more variables
            variables = []
            while self.current_token.type == 'ID':
                variables.append(ASTNode('ID', self.current_token.value))
                self.consume('ID')
            
            if not variables:
                self.error('ID')
            
            # Add variables to the lambda node
            for var in variables[:-1]:
                lambda_node = ASTNode('lambda')
                node.add_child(var)
                node.add_child(lambda_node)
                node = lambda_node
            
            node.add_child(variables[-1])
            
            if self.current_token.type != '.':
                self.error('.')
            self.consume('.')
            
            node.add_child(self.parse_e())
            return node
        else:
            return self.parse_ew()