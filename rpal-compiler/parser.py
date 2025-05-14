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
        self.current_token = self.tokens[0] if tokens else None
    
    def error(self, expected=None):
        token = self.current_token
        if token:
            if expected:
                raise Exception(f"Expected {expected}, got {token.type} at line {token.line}, column {token.column}")
            else:
                raise Exception(f"Unexpected token {token.type} at line {token.line}, column {token.column}")
        else:
            if expected:
                raise Exception(f"Expected {expected}, but reached end of input")
            else:
                raise Exception("Unexpected end of input")
    
    def consume(self, expected_type=None):
        """Consume the current token and advance to the next one"""
        if not self.current_token:
            if expected_type:
                self.error(expected_type)
            else:
                self.error()
            return
            
        if expected_type and self.current_token.type != expected_type:
            self.error(expected_type)
        
        if self.current_token_index < len(self.tokens) - 1:
            self.current_token_index += 1
            self.current_token = self.tokens[self.current_token_index]
        else:
            # Add an EOF token for better parsing at the end
            self.current_token = None

    # RPAL grammar implementation
    # E -> 'let' D 'in' E | 'fn' Vb+ '.' E | Ew
    def parse_e(self):
        if self.current_token and self.current_token.type == 'let':
            node = ASTNode('let')
            self.consume('let')
            
            # Parse all definitions until 'in'
            while self.current_token and self.current_token.type not in ['in', 'where']:
                node.add_child(self.parse_d())
                
                # Check for proper termination
                if not self.current_token:
                    raise Exception("Unexpected end of input in let expression")
            
            # Handle where clause if present
            if self.current_token and self.current_token.type == 'where':
                self.consume('where')
                where_node = ASTNode('where')
                while self.current_token and self.current_token.type != 'in':
                    where_node.add_child(self.parse_d())
                node.add_child(where_node)
            
            # Require 'in'
            if not self.current_token or self.current_token.type != 'in':
                found = self.current_token.type if self.current_token else "end of input"
                raise Exception(
                    f"Missing 'in' after definitions at line {self.current_token.line if self.current_token else 'unknown'}\n"
                    f"Found '{found}' instead"
                )
            self.consume('in')
            
            node.add_child(self.parse_e())
            return node
        
        elif self.current_token and self.current_token.type == 'fn':
            node = ASTNode('lambda')
            self.consume('fn')
            
            # Add variables to the lambda node
            while self.current_token and self.current_token.type != '.':
                node.add_child(self.parse_vb())
            
            if not self.current_token or self.current_token.type != '.':
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
            
            # Parse definitions until end of where block
            while self.current_token and self.current_token.type not in ['in', 'EOF']:
                where_node.add_child(self.parse_d())
            
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
    
    # Parse function application 
    def parse_function_application(self):
        # This should handle cases like "foo(a, b, c)" by creating gamma nodes
        func_name = ASTNode('ID', self.current_token.value)
        self.consume('ID')
        self.consume('(')
        
        # Parse first argument
        if self.current_token.type != ')':
            arg = self.parse_e()
            app_node = ASTNode('gamma')
            app_node.add_child(func_name)
            app_node.add_child(arg)
            
            # Parse additional arguments
            while self.current_token.type == ',':
                self.consume(',')
                arg = self.parse_e()
                
                # For each additional argument, wrap in another gamma
                new_app = ASTNode('gamma')
                new_app.add_child(app_node)
                new_app.add_child(arg)
                app_node = new_app
        else:
            # No arguments, just function name
            app_node = func_name
        
        self.consume(')')
        return app_node
    
    # R -> Rn | '(' E ')' | 'true' | 'false' | 'nil' | 'dummy' | INT | STR | ID | '(' E (',' E)+ ')'
    def parse_r(self):
        if not self.current_token:
            self.error("Expected a term, but reached end of input")
            
        if self.current_token.type == '(':
            self.consume('(')
            expr = self.parse_e()
            
            # Check if it's a tuple
            if self.current_token and self.current_token.type == ',':
                tuple_node = ASTNode('tau')
                tuple_node.add_child(expr)
                
                while self.current_token and self.current_token.type == ',':
                    self.consume(',')
                    tuple_node.add_child(self.parse_e())
                
                if not self.current_token or self.current_token.type != ')':
                    self.error(')')
                self.consume(')')
                return tuple_node
            
            if not self.current_token or self.current_token.type != ')':
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
            id_value = self.current_token.value
            id_node = ASTNode('ID', id_value)
            self.consume('ID')
            
            # Check if it's a function call - look ahead for '('
            if self.current_token and self.current_token.type == '(':
                self.consume('(')
                
                # No arguments case
                if self.current_token and self.current_token.type == ')':
                    self.consume(')')
                    return id_node
                
                # Parse first argument
                arg = self.parse_e()
                gamma_node = ASTNode('gamma')
                gamma_node.add_child(id_node)
                gamma_node.add_child(arg)
                
                # Parse additional arguments with nested gamma nodes
                while self.current_token and self.current_token.type == ',':
                    self.consume(',')
                    next_arg = self.parse_e()
                    
                    # Create a new gamma node for each argument
                    new_gamma = ASTNode('gamma')
                    new_gamma.add_child(gamma_node)
                    new_gamma.add_child(next_arg)
                    gamma_node = new_gamma
                
                if not self.current_token or self.current_token.type != ')':
                    self.error(')')
                self.consume(')')
                
                return gamma_node
            
            return id_node
            
        else:
            # If none of the above, try to parse as a function application
            try:
                return self.parse_application()
            except Exception:
                self.error("Unexpected token in expression")
    
    # Parse function application
    def parse_application(self):
        # Save current position in case we need to backtrack
        saved_index = self.current_token_index
        saved_token = self.current_token
        
        try:
            # Try to parse as function followed by argument
            func = self.parse_r()
            
            # If we successfully parsed a function and there's more input,
            # try to parse an argument
            if self.current_token and self.current_token.type in ['ID', 'INT', 'STR', '(', 'true', 'false', 'nil', 'dummy']:
                arg = self.parse_r()
                gamma_node = ASTNode('gamma')
                gamma_node.add_child(func)
                gamma_node.add_child(arg)
                return gamma_node
            
            # No valid argument found, not a function application
            # Restore state and return the function
            self.current_token_index = saved_index
            self.current_token = saved_token
            
            return func
            
        except Exception:
            # If parsing fails, restore position
            self.current_token_index = saved_index
            self.current_token = saved_token
            raise
    
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
        if self.current_token and self.current_token.type == 'rec':
            rec_node = ASTNode('rec')
            self.consume('rec')
            rec_node.add_child(self.parse_dr())
            return rec_node
        
        return self.parse_dr()
    
    # Dr -> 'let' D 'in' Dr | Db
    def parse_dr(self):
        if self.current_token and self.current_token.type == 'let':
            let_node = ASTNode('let')
            self.consume('let')
            let_node.add_child(self.parse_d())
            
            if not self.current_token or self.current_token.type != 'in':
                self.error('in')
            self.consume('in')
            
            let_node.add_child(self.parse_dr())
            return let_node
        
        return self.parse_db()
    
    # Db -> Vl '=' E | '(' D ')' | ID '(' Vb* ')' '=' E
    def parse_db(self):
        if not self.current_token:
            self.error("Expected definition, but reached end of input")
            
        if self.current_token.type == '(':
            self.consume('(')
            d_node = self.parse_d()
            
            if not self.current_token or self.current_token.type != ')':
                self.error(')')
            self.consume(')')
            
            return d_node
        
        # Check for function definition pattern: ID '(' ... ')' '='
        # Need to look ahead safely
        elif (self.current_token.type == 'ID' and 
              self.current_token_index + 1 < len(self.tokens) and 
              self.tokens[self.current_token_index + 1].type == '('):
            
            # Function definition
            func_name = ASTNode('ID', self.current_token.value)
            self.consume('ID')  # Consume function name
            self.consume('(')   # Consume opening parenthesis
            
            # Create function form node
            func_form = ASTNode('function_form')
            func_form.add_child(func_name)
            
            # Parse parameters (if any)
            if self.current_token and self.current_token.type != ')':
                param = ASTNode('ID', self.current_token.value)
                self.consume('ID')
                func_form.add_child(param)
                
                while self.current_token and self.current_token.type == ',':
                    self.consume(',')
                    if not self.current_token or self.current_token.type != 'ID':
                        self.error('ID')
                    param = ASTNode('ID', self.current_token.value)
                    self.consume('ID')
                    func_form.add_child(param)
            
            # Consume closing parenthesis
            if not self.current_token or self.current_token.type != ')':
                self.error(')')
            self.consume(')')
            
            # Consume equals sign
            if not self.current_token or self.current_token.type != '=':
                self.error('=')
            self.consume('=')
            
            # Parse function body
            body = self.parse_e()
            func_form.add_child(body)
            
            return func_form
        
        else:
            # Variable definition
            vl_node = self.parse_vl()
            
            if not self.current_token or self.current_token.type != '=':
                self.error('=')
            self.consume('=')
            
            equals_node = ASTNode('=')
            equals_node.add_child(vl_node)
            equals_node.add_child(self.parse_e())
            
            return equals_node
    
    # Vl -> ID | '(' Vl ')'
    def parse_vl(self):
        if not self.current_token:
            self.error("Expected variable, but reached end of input")
            
        if self.current_token.type == 'ID':
            id_node = ASTNode('ID', self.current_token.value)
            self.consume('ID')
            return id_node
        
        elif self.current_token.type == '(':
            self.consume('(')
            vl_node = self.parse_vl()
            
            if not self.current_token or self.current_token.type != ')':
                self.error(')')
            self.consume(')')
            
            return vl_node
        
        else:
            self.error('ID or (')
    
    # Vb -> ID | '(' Vb ')'
    def parse_vb(self):
        if not self.current_token:
            self.error("Expected variable binding, but reached end of input")
            
        if self.current_token.type == 'ID':
            id_node = ASTNode('ID', self.current_token.value)
            self.consume('ID')
            return id_node
        
        elif self.current_token.type == '(':
            self.consume('(')
            vb_node = self.parse_vb()
            
            if not self.current_token or self.current_token.type != ')':
                self.error(')')
            self.consume(')')
            
            return vb_node
        
        else:
            self.error('ID or (')
    
    def parse(self):
        """Entry point for parsing"""
        ast = self.parse_e()
        
        # Check if we've consumed all tokens
        if self.current_token is not None:
            raise Exception(f"Unexpected token {self.current_token.type} at end of input")
            
        return ast


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