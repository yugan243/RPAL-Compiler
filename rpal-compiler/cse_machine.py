from parser import ASTNode
from standardizer import standardize_ast

class Environment:
    def __init__(self, parent=None):
        self.bindings = {}
        self.parent = parent
    
    def lookup(self, var_name):
        if var_name in self.bindings:
            return self.bindings[var_name]
        elif self.parent:
            return self.parent.lookup(var_name)
        else:
            raise Exception(f"Unbound variable: {var_name}")
    
    def bind(self, var_name, value):
        self.bindings[var_name] = value
    
    def __str__(self):
        result = "Environment:\n"
        for var, value in self.bindings.items():
            result += f"  {var}: {value}\n"
        if self.parent:
            result += "Parent " + str(self.parent)
        return result


class CSEMachine:
    def __init__(self, st):
        self.control = [st]  # Initial control structure (ST root)
        self.stack = []      # Empty stack
        self.environment = Environment()  # Initial environment
        
        # Bind primitive operations
        self.bind_primitives()
    
    def bind_primitives(self):
        """Bind primitive operations to the environment"""
        # Arithmetic operations
        self.environment.bind('+', PrimitiveFunction(self.primitive_add, 2))
        self.environment.bind('-', PrimitiveFunction(self.primitive_subtract, 2))
        self.environment.bind('*', PrimitiveFunction(self.primitive_multiply, 2))
        self.environment.bind('/', PrimitiveFunction(self.primitive_divide, 2))
        
        # Comparison operations
        self.environment.bind('eq', PrimitiveFunction(self.primitive_eq, 2))
        self.environment.bind('ne', PrimitiveFunction(self.primitive_ne, 2))
        self.environment.bind('gr', PrimitiveFunction(self.primitive_gr, 2))
        self.environment.bind('ge', PrimitiveFunction(self.primitive_ge, 2))
        self.environment.bind('ls', PrimitiveFunction(self.primitive_ls, 2))
        self.environment.bind('le', PrimitiveFunction(self.primitive_le, 2))
        
        # Logical operations
        self.environment.bind('and', PrimitiveFunction(self.primitive_and, 2))
        self.environment.bind('or', PrimitiveFunction(self.primitive_or, 2))
        self.environment.bind('not', PrimitiveFunction(self.primitive_not, 1))
        
        # Other operations
        self.environment.bind('Print', PrimitiveFunction(self.primitive_print, 1))
        self.environment.bind('Order', PrimitiveFunction(self.primitive_order, 1))
        self.environment.bind('Isinteger', PrimitiveFunction(self.primitive_isinteger, 1))
        self.environment.bind('Isstring', PrimitiveFunction(self.primitive_isstring, 1))
        self.environment.bind('Isdummy', PrimitiveFunction(self.primitive_isdummy, 1))
        self.environment.bind('Istuple', PrimitiveFunction(self.primitive_istuple, 1))
        self.environment.bind('Isfunction', PrimitiveFunction(self.primitive_isfunction, 1))
        self.environment.bind('Isbool', PrimitiveFunction(self.primitive_isbool, 1))
        self.environment.bind('Istruthvalue', PrimitiveFunction(self.primitive_istruthvalue, 1))
    
    # Primitive operation implementations
    def primitive_add(self, args):
        if len(args) != 2:
            raise Exception("+ requires exactly 2 arguments")
        return args[0] + args[1]
    
    def primitive_subtract(self, args):
        if len(args) != 2:
            raise Exception("- requires exactly 2 arguments")
        return args[0] - args[1]
    
    def primitive_multiply(self, args):
        if len(args) != 2:
            raise Exception("* requires exactly 2 arguments")
        return args[0] * args[1]
    
    def primitive_divide(self, args):
        if len(args) != 2:
            raise Exception("/ requires exactly 2 arguments")
        if args[1] == 0:
            raise Exception("Division by zero")
        return args[0] // args[1]  # Integer division
    
    def primitive_eq(self, args):
        if len(args) != 2:
            raise Exception("eq requires exactly 2 arguments")
        return args[0] == args[1]
    
    def primitive_ne(self, args):
        if len(args) != 2:
            raise Exception("ne requires exactly 2 arguments")
        return args[0] != args[1]
    
    def primitive_gr(self, args):
        if len(args) != 2:
            raise Exception("gr requires exactly 2 arguments")
        return args[0] > args[1]
    
    def primitive_ge(self, args):
        if len(args) != 2:
            raise Exception("ge requires exactly 2 arguments")
        return args[0] >= args[1]
    
    def primitive_ls(self, args):
        if len(args) != 2:
            raise Exception("ls requires exactly 2 arguments")
        return args[0] < args[1]
    
    def primitive_le(self, args):
        if len(args) != 2:
            raise Exception("le requires exactly 2 arguments")
        return args[0] <= args[1]
    
    def primitive_and(self, args):
        if len(args) != 2:
            raise Exception("and requires exactly 2 arguments")
        return args[0] and args[1]
    
    def primitive_or(self, args):
        if len(args) != 2:
            raise Exception("or requires exactly 2 arguments")
        return args[0] or args[1]
    
    def primitive_not(self, args):
        if len(args) != 1:
            raise Exception("not requires exactly 1 argument")
        return not args[0]
    
    def primitive_print(self, args):
        if len(args) != 1:
            raise Exception("Print requires exactly 1 argument")
        print(args[0])
        return args[0]
    
    def primitive_order(self, args):
        if len(args) != 1:
            raise Exception("Order requires exactly 1 argument")
        if isinstance(args[0], tuple):
            return len(args[0])
        raise Exception("Order requires a tuple argument")
    
    def primitive_isinteger(self, args):
        if len(args) != 1:
            raise Exception("Isinteger requires exactly 1 argument")
        return isinstance(args[0], int)
    
    def primitive_isstring(self, args):
        if len(args) != 1:
            raise Exception("Isstring requires exactly 1 argument")
        return isinstance(args[0], str)
    
    def primitive_isdummy(self, args):
        if len(args) != 1:
            raise Exception("Isdummy requires exactly 1 argument")
        return args[0] == "dummy"
    
    def primitive_istuple(self, args):
        if len(args) != 1:
            raise Exception("Istuple requires exactly 1 argument")
        return isinstance(args[0], tuple)
    
    def primitive_isfunction(self, args):
        if len(args) != 1:
            raise Exception("Isfunction requires exactly 1 argument")
        return isinstance(args[0], LambdaClosure) or isinstance(args[0], PrimitiveFunction)
    
    def primitive_isbool(self, args):
        if len(args) != 1:
            raise Exception("Isbool requires exactly 1 argument")
        return isinstance(args[0], bool)
    
    def primitive_istruthvalue(self, args):
        if len(args) != 1:
            raise Exception("Istruthvalue requires exactly 1 argument")
        return args[0] is True or args[0] is False
    
    def execute(self):
        """Execute the CSE machine"""
        while self.control:
            # Get current control element
            control_item = self.control.pop()
            
            # Process based on node type
            if isinstance(control_item, ASTNode):
                self.process_node(control_item)
            else:
                # This is a value, push it onto stack
                self.stack.append(control_item)
        
        # Return the final result from stack
        if self.stack:
            return self.stack[-1]
        return None
    
    def process_node(self, node):
        """Process a node in the control structure"""
        if node.type == 'INT':
            # Push integer literal onto stack
            self.stack.append(int(node.value))
        
        elif node.type == 'STR':
            # Push string literal onto stack
            self.stack.append(node.value)
        
        elif node.type == 'true':
            # Push boolean true onto stack
            self.stack.append(True)
        
        elif node.type == 'false':
            # Push boolean false onto stack
            self.stack.append(False)
        
        elif node.type == 'nil':
            # Push nil (empty tuple) onto stack
            self.stack.append(())
        
        elif node.type == 'dummy':
            # Push dummy value onto stack
            self.stack.append("dummy")
        
        elif node.type == 'ID':
            # Look up variable in environment
            value = self.environment.lookup(node.value)
            self.stack.append(value)
        
        elif node.type == 'lambda':
            # Create lambda closure
            var_node = node.children[0]
            body_node = node.children[1]
            
            # The closure captures the current environment
            closure = LambdaClosure(var_node, body_node, self.environment)
            self.stack.append(closure)
        
        elif node.type == 'gamma':
            # Function application
            # Push the function body and argument onto control
            self.control.append(ApplyControl())  # Marker for application
            self.control.append(node.children[1])  # Argument
            self.control.append(node.children[0])  # Function
        
        elif node.type == 'tau':
            # Tuple construction
            # Start with empty tuple
            if not node.children:
                self.stack.append(())
            else:
                # Mark control for tuple construction
                self.control.append(TupleControl(len(node.children)))
                # Push tuple elements in reverse order
                for child in reversed(node.children):
                    self.control.append(child)
        
        elif node.type == '=':
            # Variable binding
            var_node = node.children[0]
            val_node = node.children[1]
            
            # Process value first
            self.control.append(BindControl(var_node.value))
            self.control.append(val_node)
        
        elif node.type == 'rec':
            # Recursive binding
            binding_node = node.children[0]
            
            if binding_node.type == '=':
                var_node = binding_node.children[0]
                val_node = binding_node.children[1]
                
                # Create recursive binding
                self.control.append(RecBindControl(var_node.value))
                self.control.append(val_node)
            else:
                raise Exception("Rec expects a binding node")
        
        elif node.type == ',':
            # Sequence of operations
            # Push second operation, then first
            self.control.append(node.children[1])
            self.control.append(node.children[0])
        
        else:
            raise Exception(f"Unknown node type: {node.type}")
    
    def apply(self):
        """Apply a function to an argument"""
        # Pop argument and function from stack
        arg = self.stack.pop()
        func = self.stack.pop()
        
        if isinstance(func, PrimitiveFunction):
            # Apply primitive function
            result = func.apply([arg])
            self.stack.append(result)
        
        elif isinstance(func, LambdaClosure):
            # Apply lambda closure
            # Create new environment with closure's environment as parent
            new_env = Environment(func.env)
            
            # Bind argument to parameter
            var_name = func.var_node.value
            new_env.bind(var_name, arg)
            
            # Save current environment
            old_env = self.environment
            
            # Set new environment
            self.environment = new_env
            
            # Push body to control
            self.control.append(RestoreEnvControl(old_env))
            self.control.append(func.body_node)
        
        else:
            raise Exception(f"Cannot apply non-function: {func}")


class PrimitiveFunction:
    """Represents a primitive (built-in) function"""
    def __init__(self, func, arity):
        self.func = func
        self.arity = arity
        self.args = []
    
    def apply(self, args):
        """Apply function to arguments"""
        self.args.extend(args)
        
        if len(self.args) >= self.arity:
            result = self.func(self.args[:self.arity])
            self.args = self.args[self.arity:]
            return result
        
        # Return partially applied function
        return self
    
    def __str__(self):
        return f"<primitive function>"


class LambdaClosure:
    """Represents a lambda closure (function with environment)"""
    def __init__(self, var_node, body_node, env):
        self.var_node = var_node
        self.body_node = body_node
        self.env = env
    
    def __str__(self):
        return f"<lambda {self.var_node.value}.{self.body_node}>"


# Control markers for special operations
class ApplyControl:
    """Marker for function application"""
    pass


class TupleControl:
    """Marker for tuple construction"""
    def __init__(self, size):
        self.size = size


class BindControl:
    """Marker for variable binding"""
    def __init__(self, var_name):
        self.var_name = var_name


class RecBindControl:
    """Marker for recursive binding"""
    def __init__(self, var_name):
        self.var_name = var_name


class RestoreEnvControl:
    """Marker for environment restoration"""
    def __init__(self, env):
        self.env = env


def run_cse_machine(st):
    """Run the CSE machine on a standardized tree"""
    machine = CSEMachine(st)
    result = machine.execute()
    return result


def execute_rpal(filename, print_ast=False):
    """Execute an RPAL program from a file"""
    from parser import parse_file
    
    # Parse input file to AST
    ast = parse_file(filename)
    
    if print_ast:
        print("Abstract Syntax Tree:")
        ast.print_ast()
        return
    
    # Standardize AST to ST
    st = standardize_ast(ast)
    
    # Execute ST
    run_cse_machine(st)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python cse_machine.py <filename> [-ast]")
        sys.exit(1)
    
    filename = sys.argv[1]
    print_ast = False
    
    if len(sys.argv) > 2 and sys.argv[2] == "-ast":
        print_ast = True
    
    execute_rpal(filename, print_ast)