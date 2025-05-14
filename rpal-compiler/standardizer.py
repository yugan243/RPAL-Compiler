from parser import ASTNode, parse_file

class Standardizer:
    def __init__(self, ast):
        self.ast = ast
        # Counter for generating unique variable names
        self.unique_counter = 0
    
    def generate_unique_var(self):
        """Generate a unique variable name"""
        self.unique_counter += 1
        return f"x_{self.unique_counter}"
    
    def standardize(self):
        """Convert AST to ST"""
        return self.standardize_node(self.ast)
    
    def standardize_node(self, node):
        """Recursively standardize a node in the AST"""
        if node.type == 'let':
            return self.standardize_let(node)
        elif node.type == 'where':
            return self.standardize_where(node)
        elif node.type == 'function_form':
            return self.standardize_function_form(node)
        elif node.type == 'lambda':
            return self.standardize_lambda(node)
        elif node.type == 'and':
            return self.standardize_and(node)
        elif node.type == 'rec':
            return self.standardize_rec(node)
        elif node.type == '=':
            return self.standardize_equals(node)
        elif node.type == '->':
            return self.standardize_conditional(node)
        elif node.type == 'tau':
            return self.standardize_tau(node)
        elif node.type == 'gamma':
            return self.standardize_gamma(node)
        else:
            # For simple nodes (ID, INT, STR, etc.), standardize children but keep node type
            new_node = ASTNode(node.type, node.value)
            for child in node.children:
                new_node.add_child(self.standardize_node(child))
            return new_node
    
    def standardize_let(self, node):
        """Standardize a let expression: let D in E => (lambda V.E)(D')"""
        # Standardize the definition part (D)
        d_node = self.standardize_node(node.children[0])
        
        # Standardize the expression part (E)
        e_node = self.standardize_node(node.children[1])
        
        # If the definition is a simple binding (P=E), transform to (lambda P.E')(E'')
        if d_node.type == '=':
            # Create lambda node
            lambda_node = ASTNode('lambda')
            lambda_node.add_child(d_node.children[0])  # P (pattern)
            lambda_node.add_child(e_node)  # E' (standardized expression)
            
            # Create gamma node for application
            gamma_node = ASTNode('gamma')
            gamma_node.add_child(lambda_node)
            gamma_node.add_child(d_node.children[1])  # E'' (standardized expression in binding)
            
            return gamma_node
        
        # Handle more complex definitions (e.g., function definitions)
        # This is a simplified implementation - real implementation would handle various cases
        lambda_node = ASTNode('lambda')
        lambda_node.add_child(ASTNode('ID', 'x'))  # Placeholder variable
        lambda_node.add_child(e_node)
        
        gamma_node = ASTNode('gamma')
        gamma_node.add_child(lambda_node)
        gamma_node.add_child(d_node)
        
        return gamma_node
    
    def standardize_where(self, node):
        """Standardize a where expression: E where D => (lambda V.E)(D')"""
        # This is similar to let, but with order reversed
        e_node = self.standardize_node(node.children[0])  # E
        d_node = self.standardize_node(node.children[1])  # D
        
        # Handle simple binding case
        if d_node.type == '=':
            lambda_node = ASTNode('lambda')
            lambda_node.add_child(d_node.children[0])  # Pattern
            lambda_node.add_child(e_node)
            
            gamma_node = ASTNode('gamma')
            gamma_node.add_child(lambda_node)
            gamma_node.add_child(d_node.children[1])  # Expression
            
            return gamma_node
        
        # Handle more complex definitions
        lambda_node = ASTNode('lambda')
        lambda_node.add_child(ASTNode('ID', 'x'))  # Placeholder
        lambda_node.add_child(e_node)
        
        gamma_node = ASTNode('gamma')
        gamma_node.add_child(lambda_node)
        gamma_node.add_child(d_node)
        
        return gamma_node
    
    def standardize_function_form(self, node):
        """Standardize function form: f(x1,...,xn) = E => f = lambda x1,...,xn.E"""
        # Extract function name and parameters
        func_name = node.children[0]
        params = node.children[1:-1]  # All children except first and last
        body = node.children[-1]
        
        # Standardize body
        std_body = self.standardize_node(body)
        
        # Create nested lambda expression
        current = std_body
        for param in reversed(params):
            lambda_node = ASTNode('lambda')
            lambda_node.add_child(param)
            lambda_node.add_child(current)
            current = lambda_node
        
        # Create equals node
        equals_node = ASTNode('=')
        equals_node.add_child(func_name)
        equals_node.add_child(current)
        
        return equals_node
    
    def standardize_lambda(self, node):
        """Standardize lambda expression: lambda x.E => lambda x.E'"""
        new_node = ASTNode('lambda')
        new_node.add_child(node.children[0])  # Variable
        new_node.add_child(self.standardize_node(node.children[1]))  # Body
        return new_node
    
    def standardize_and(self, node):
        """Standardize and expression: D1 and D2 => comma(D1', D2')"""
        comma_node = ASTNode(',')
        comma_node.add_child(self.standardize_node(node.children[0]))
        comma_node.add_child(self.standardize_node(node.children[1]))
        return comma_node
    
    def standardize_rec(self, node):
        """Standardize rec expression: rec D => rec D'"""
        rec_node = ASTNode('rec')
        rec_node.add_child(self.standardize_node(node.children[0]))
        return rec_node
    
    def standardize_equals(self, node):
        """Standardize equals expression: P = E => P = E'"""
        equals_node = ASTNode('=')
        equals_node.add_child(self.standardize_node(node.children[0]))
        equals_node.add_child(self.standardize_node(node.children[1]))
        return equals_node
    
    def standardize_conditional(self, node):
        """Standardize conditional: E1 -> E2 | E3 => gamma(gamma(->',E1'),E2'),E3'"""
        cond = self.standardize_node(node.children[0])
        then_part = self.standardize_node(node.children[1])
        
        # Check if there's an else part, otherwise use dummy
        else_part_node = node.children[2] if len(node.children) > 2 else ASTNode('dummy')
        else_part = self.standardize_node(else_part_node)
        
        # Create gamma nodes for application
        gamma1 = ASTNode('gamma')
        gamma1.add_child(ASTNode('->', None))  # Conditional operator
        gamma1.add_child(cond)
        
        gamma2 = ASTNode('gamma')
        gamma2.add_child(gamma1)
        gamma2.add_child(then_part)
        
        # Final application with else part
        gamma3 = ASTNode('gamma')
        gamma3.add_child(gamma2)
        gamma3.add_child(else_part)
        
        return gamma3
    
    def standardize_tau(self, node):
        """Standardize tuple expression: (E1,...,En) => gamma(gamma(tau,E1'),...,En')"""
        if not node.children:
            return ASTNode('nil')
        
        # Standardize all elements
        elements = [self.standardize_node(child) for child in node.children]
        
        # Create tau node
        tau_node = ASTNode('tau')
        
        # Create nested gamma nodes
        current = tau_node
        for element in elements:
            gamma_node = ASTNode('gamma')
            gamma_node.add_child(current)
            gamma_node.add_child(element)
            current = gamma_node
        
        return current
    
    def standardize_gamma(self, node):
        """Standardize function application: E1 E2 => gamma(E1',E2')"""
        gamma_node = ASTNode('gamma')
        gamma_node.add_child(self.standardize_node(node.children[0]))
        gamma_node.add_child(self.standardize_node(node.children[1]))
        return gamma_node


def standardize_ast(ast):
    standardizer = Standardizer(ast)
    return standardizer.standardize()

# Test the standardizer
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python standardizer.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]
    ast = parse_file(filename)
    st = standardize_ast(ast)
    
    print("Standardized Tree:")
    st.print_ast()