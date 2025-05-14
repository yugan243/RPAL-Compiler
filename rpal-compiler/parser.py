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
            
            # Parse definition D
            d_node = self.parse_d()
            node.add_child(d_node)
            
            # Require 'in'
            if self.current_token.type != 'in':
                self.error('in')
            self.consume('in')
            
            # Parse expression E
            e_node = self.parse_e()
            node.add_child(e_node)
            
            return node
        
        elif self.current_token.type == 'fn':
            node = ASTNode('lambda')
            self.consume('fn')
            
            # Parse variable bindings
            while self.current_token.type != '.':
                vb_node = self.parse_vb()
                node.add_child(vb_node)
                
                if not self.current_token:
                    self.error('.')
            
            self.consume('.')
            
            # Parse body expression
            body_node = self.parse_e()
            node.add_child(body_node)
            
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
            tau_node = ASTNode('tau')
            self.consume(',')
            tau_node.add_child(left)
            tau_node.add_child(self.parse_ta())
            left = tau_node
        
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
    
    # Ap -> R [ R ]*  (function application)
    def parse_ap(self):
        left = self.parse_r()
        
        # Function application (only if there's another R term)
        if self.current_token and self.current_token.type in ['(', 'ID', 'INT', 'STR', 'true', 'false', 'nil', 'dummy']:
            # Check if it's a function application
            if self._is_r_start():
                gamma_node = ASTNode('gamma')
                gamma_node.add_child(left)
                gamma_node.add_child(self.parse_r())
                return gamma_node
        
        return left
    
    def _is_r_start(self):
        """Check if current token can start an R expression"""
        if not self.current_token:
            return False
        return self.current_token.type in ['(', 'ID', 'INT', 'STR', 'true', 'false', 'nil', 'dummy']
    
    # R -> '(' E ')' | 'true' | 'false' | 'nil' | 'dummy' | INT | STR | ID
    def parse_r(self):
        if self.current_token.type == '(':
            self.consume('(')
            
            # Parse the expression inside parentheses
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
            
            # Close the parentheses
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
            node = ASTNode('ID', self.current_token.value)
            self.consume('ID')
            return node
            
        else:
            self.error("R expression")
            
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
    
    # Db -> Vl '=' E | '(' D ')' | ID '(' Vb+ ')' '=' E
    def parse_db(self):
        if self.current_token and self.current_token.type == '(':
            self.consume('(')
            d_node = self.parse_d()
            
            if not self.current_token or self.current_token.type != ')':
                self.error(')')
            self.consume(')')
            
            return d_node
        
        # Check for function definition: ID ( params ) = E
        elif (self.current_token and self.current_token.type == 'ID' and 
              self.current_token_index + 1 < len(self.tokens) and 
              self.tokens[self.current_token_index + 1].type == '('):
            
            func_name = ASTNode('ID', self.current_token.value)
            self.consume('ID')
            self.consume('(')
            
            # Parse parameters
            params = []
            if self.current_token and self.current_token.type != ')':
                params.append(self.parse_vb())
                
                while self.current_token and self.current_token.type == ',':
                    self.consume(',')
                    params.append(self.parse_vb())
            
            if not self.current_token or self.current_token.type != ')':
                self.error(')')
            self.consume(')')
            
            if not self.current_token or self.current_token.type != '=':
                self.error('=')
            self.consume('=')
            
            body = self.parse_e()
            
            # Construct function form node
            func_form = ASTNode('function_form')
            func_form.add_child(func_name)
            
            for param in params:
                func_form.add_child(param)
                
            func_form.add_child(body)
            
            return func_form
            
        else:
            # Simple variable definition: Vl = E
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
        if self.current_token and self.current_token.type == 'ID':
            id_node = ASTNode('ID', self.current_token.value)
            self.consume('ID')
            return id_node
        
        elif self.current_token and self.current_token.type == '(':
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
        if self.current_token and self.current_token.type == 'ID':
            id_node = ASTNode('ID', self.current_token.value)
            self.consume('ID')
            return id_node
        
        elif self.current_token and self.current_token.type == '(':
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
        
        # Ensure we've consumed all tokens except EOF
        if self.current_token and self.current_token.type != 'EOF':
            self.error("end of input")
            
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