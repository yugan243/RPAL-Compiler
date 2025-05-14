from lexer import tokenize_file

class ASTNode:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
        self.children = []
    
    def add_child(self, node):
        self.children.append(node)
        return node
    
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
        """Consume the current token and advance to the next one"""
        if expected_type and self.current_token.type != expected_type:
            self.error(expected_type)
        
        if self.current_token_index < len(self.tokens) - 1:
            self.current_token_index += 1
            self.current_token = self.tokens[self.current_token_index]
        else:
            self.current_token = None

    # RPAL grammar implementation
    # E -> 'let' D 'in' E | 'fn' Vb+ '.' E | Ew
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
    
    # Ew -> T 'where' Dr | T
    def parse_ew(self):
        t_node = self.parse_t()
        
        if self.current_token and self.current_token.type == 'where':
            where_node = ASTNode('where')
            self.consume('where')
            where_node.add_child(t_node)
            where_node.add_child(self.parse_dr())
            return where_node
        
        return t_node
    
    # T -> Ta ( ',' Ta )*
    def parse_t(self):
        left = self.parse_ta()
        
        while self.current_token and self.current_token.type == ',':
            comma_node = ASTNode('tau')
            self.consume(',')
            comma_node.add_child(left)
            comma_node.add_child(self.parse_ta())
            left = comma_node
        
        return left
    
    # Ta -> Tc ( '->' Tc | '=>' Tc )*
    def parse_ta(self):
        left = self.parse_tc()
        
        while self.current_token and self.current_token.type == '->':
            arrow_node = ASTNode('->')
            self.consume('->')
            arrow_node.add_child(left)
            arrow_node.add_child(self.parse_tc())
            left = arrow_node
        
        return left
    
    # Tc -> B ( '&' B )*
    def parse_tc(self):
        left = self.parse_b()
        
        while self.current_token and self.current_token.type == '&':
            and_node = ASTNode('and')
            self.consume('&')
            and_node.add_child(left)
            and_node.add_child(self.parse_b())
            left = and_node
        
        return left
    
    # B -> Bt ( 'or' Bt )*
    def parse_b(self):
        left = self.parse_bt()
        
        while self.current_token and self.current_token.type == 'or':
            or_node = ASTNode('or')
            self.consume('or')
            or_node.add_child(left)
            or_node.add_child(self.parse_bt())
            left = or_node
        
        return left
    
    # Bt -> Bs [ 'not' Bs ]*
    def parse_bt(self):
        left = self.parse_bs()
        
        if self.current_token and self.current_token.type == 'not':
            not_node = ASTNode('not')
            self.consume('not')
            not_node.add_child(left)
            not_node.add_child(self.parse_bs())
            return not_node
        
        return left
    
    # Bs -> A ( 'gr' A | '>' A | 'ge' A | '>=' A | 'ls' A | '<' A | 'le' A | '<=' A | 'eq' A | '=' A | 'ne' A | '!=' A )*
    def parse_bs(self):
        left = self.parse_a()
        
        comparison_ops = {
            'gr': 'gr', '>': 'gr',
            'ge': 'ge', '>=': 'ge',
            'ls': 'ls', '<': 'ls',
            'le': 'le', '<=': 'le',
            'eq': 'eq', '=': 'eq',
            'ne': 'ne', '!=': 'ne'
        }
        
        if self.current_token and self.current_token.type in comparison_ops:
            op_type = comparison_ops[self.current_token.type]
            op_node = ASTNode(op_type)
            self.consume(self.current_token.type)
            op_node.add_child(left)
            op_node.add_child(self.parse_a())
            return op_node
        
        return left
    
    # A -> At ( '+' At | '-' At )*
    def parse_a(self):
        left = self.parse_at()
        
        while self.current_token and self.current_token.type in ['+', '-']:
            op_type = self.current_token.type
            op_node = ASTNode(op_type)
            self.consume(op_type)
            op_node.add_child(left)
            op_node.add_child(self.parse_at())
            left = op_node
        
        return left
    
    # At -> Af ( '*' Af | '/' Af | '**' Af )*
    def parse_at(self):
        left = self.parse_af()
        
        while self.current_token and self.current_token.type in ['*', '/']:
            op_type = self.current_token.type
            op_node = ASTNode(op_type)
            self.consume(op_type)
            op_node.add_child(left)
            op_node.add_child(self.parse_af())
            left = op_node
        
        return left
    
    # Af -> Ap [ '@' Ap ]*
    def parse_af(self):
        left = self.parse_ap()
        
        if self.current_token and self.current_token.type == '@':
            at_node = ASTNode('@')
            self.consume('@')
            at_node.add_child(left)
            at_node.add_child(self.parse_ap())
            return at_node
        
        return left
    
    # Ap -> R [ '!' R ]*
    def parse_ap(self):
        left = self.parse_r()
        
        if self.current_token and self.current_token.type == '!':
            bang_node = ASTNode('!')
            self.consume('!')
            bang_node.add_child(left)
            bang_node.add_child(self.parse_r())
            return bang_node
        
        return left
    
    # R -> Rn | '(' E ')' | 'true' | 'false' | 'nil' | 'dummy' | INT | STR | ID | '(' E (',' E)+ ')'
    def parse_r(self):
        if self.current_token.type == '(':
            self.consume('(')
            expr = self.parse_e()
            
            # Check if it's a tuple
            if self.current_token.type == ',':
                tuple_node = ASTNode('tau')
                tuple_node.add_child(expr)
                
                while self.current_token.type == ',':
                    self.consume(',')
                    tuple_node.add_child(self.parse_e())
                
                if self.current_token.type != ')':
                    self.error(')')
                self.consume(')')
                return tuple_node
            
            if self.current_token.type != ')':
                self.error(')')
            self.consume(')')
            return expr
        
        elif self.current_token.type == 'true':
            node = ASTNode('true')
            self.consume('true')
            return node
        
        elif self.current_token.type == 'false':
            node = ASTNode('false')
            self.consume('false')
            return node
        
        elif self.current_token.type == 'nil':
            node = ASTNode('nil')
            self.consume('nil')
            return node
        
        elif self.current_token.type == 'dummy':
            node = ASTNode('dummy')
            self.consume('dummy')
            return node
        
        elif self.current_token.type == 'INT':
            node = ASTNode('INT', self.current_token.value)
            self.consume('INT')
            return node
        
        elif self.current_token.type == 'STR':
            node = ASTNode('STR', self.current_token.value)
            self.consume('STR')
            return node
        
        elif self.current_token.type == 'ID':
            node = ASTNode('ID', self.current_token.value)
            self.consume('ID')
            return node
        
        else:
            return self.parse_rn()
    
    # Rn -> R Rn | epsilon
    def parse_rn(self):
        # Implementation for function application
        # This is a simplification - actual implementation would be more complex
        if self.current_token and self.current_token.type in ['ID', 'INT', 'STR', '(', 'true', 'false', 'nil', 'dummy']:
            func = self.parse_r()
            arg = self.parse_r()
            gamma_node = ASTNode('gamma')
            gamma_node.add_child(func)
            gamma_node.add_child(arg)
            return gamma_node
        
        self.error()
    
    # D -> Da ( 'and' Da )*
    def parse_d(self):
        left = self.parse_da()
        
        while self.current_token and self.current_token.type == 'and':
            and_node = ASTNode('and')
            self.consume('and')
            and_node.add_child(left)
            and_node.add_child(self.parse_da())
            left = and_node
        
        return left
    
    # Da -> Dr | 'rec' Dr
    def parse_da(self):
        if self.current_token.type == 'rec':
            rec_node = ASTNode('rec')
            self.consume('rec')
            rec_node.add_child(self.parse_dr())
            return rec_node
        
        return self.parse_dr()
    
    # Dr -> 'let' D 'in' Dr | Db
    def parse_dr(self):
        if self.current_token.type == 'let':
            let_node = ASTNode('let')
            self.consume('let')
            let_node.add_child(self.parse_d())
            
            if self.current_token.type != 'in':
                self.error('in')
            self.consume('in')
            
            let_node.add_child(self.parse_dr())
            return let_node
        
        return self.parse_db()
    
    # Db -> Vl '=' E | '(' D ')' | ID '(' Vb+ ')' '=' E
    def parse_db(self):
        if self.current_token.type == '(':
            self.consume('(')
            d_node = self.parse_d()
            
            if self.current_token.type != ')':
                self.error(')')
            self.consume(')')
            
            return d_node
        
        elif self.current_token.type == 'ID' and self.tokens[self.current_token_index + 1].type == '(':
            # Function definition
            function_name = ASTNode('ID', self.current_token.value)
            self.consume('ID')
            self.consume('(')
            
            # Parse parameters
            parameters = []
            if self.current_token.type == 'ID':
                parameters.append(ASTNode('ID', self.current_token.value))
                self.consume('ID')
                
                while self.current_token.type == ',':
                    self.consume(',')
                    if self.current_token.type != 'ID':
                        self.error('ID')
                    parameters.append(ASTNode('ID', self.current_token.value))
                    self.consume('ID')
            
            if self.current_token.type != ')':
                self.error(')')
            self.consume(')')
            
            if self.current_token.type != '=':
                self.error('=')
            self.consume('=')
            
            function_body = self.parse_e()
            
            # Build function form node
            function_form = ASTNode('function_form')
            function_form.add_child(function_name)
            
            for param in parameters:
                function_form.add_child(param)
            
            function_form.add_child(function_body)
            
            return function_form
        
        else:
            # Variable definition
            vl_node = self.parse_vl()
            
            if self.current_token.type != '=':
                self.error('=')
            self.consume('=')
            
            equals_node = ASTNode('=')
            equals_node.add_child(vl_node)
            equals_node.add_child(self.parse_e())
            
            return equals_node
    
    # Vl -> ID | '(' Vl ')'
    def parse_vl(self):
        if self.current_token.type == 'ID':
            id_node = ASTNode('ID', self.current_token.value)
            self.consume('ID')
            return id_node
        
        elif self.current_token.type == '(':
            self.consume('(')
            vl_node = self.parse_vl()
            
            if self.current_token.type != ')':
                self.error(')')
            self.consume(')')
            
            return vl_node
        
        else:
            self.error('ID or (')
    
    # Vb -> ID | '(' Vb ')'
    def parse_vb(self):
        if self.current_token.type == 'ID':
            id_node = ASTNode('ID', self.current_token.value)
            self.consume('ID')
            return id_node
        
        elif self.current_token.type == '(':
            self.consume('(')
            vb_node = self.parse_vb()
            
            if self.current_token.type != ')':
                self.error(')')
            self.consume(')')
            
            return vb_node
        
        else:
            self.error('ID or (')
    
    def parse(self):
        """Entry point for parsing"""
        return self.parse_e()


def parse_file(filename):
    tokens = tokenize_file(filename)
    parser = Parser(tokens)
    return parser.parse()

# Test the parser
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python parser.py <filename> [-ast]")
        sys.exit(1)
    
    filename = sys.argv[1]
    print_ast = False
    
    if len(sys.argv) > 2 and sys.argv[2] == "-ast":
        print_ast = True
    
    ast = parse_file(filename)
    
    if print_ast:
        ast.print_ast()