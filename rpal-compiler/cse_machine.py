from parser import ASTNode

class CSEMachine:
    def __init__(self, st):
        self.control = [st]  # Control stack
        self.stack = []      # Value stack
        self.env = [{}]      # Environment stack
        self.builtin_functions = {
            'Print': lambda x: x,
            'Order': lambda x: len(x) if isinstance(x, list) else 0,
            'IsTuple': lambda x: 1 if isinstance(x, list) else 0,
            'IsInteger': lambda x: 1 if isinstance(x, int) else 0,
            'IsString': lambda x: 1 if isinstance(x, str) else 0,
            'IsFunction': lambda x: 1 if isinstance(x, tuple) and x[0].type == 'lambda' else 0
        }

    def evaluate(self):
        while self.control:
            node = self.control.pop(0)

            # Literals
            if node.type == 'INT':
                self.stack.append(int(node.value))

            elif node.type == 'STR':
                self.stack.append(str(node.value))

            elif node.type == 'true':
                self.stack.append(1)

            elif node.type == 'false':
                self.stack.append(0)

            # Variables
            elif node.type == 'ID':
                if node.value in self.builtin_functions:
                    self.stack.append(self.builtin_functions[node.value])
                else:
                    for env in reversed(self.env):
                        if node.value in env:
                            self.stack.append(env[node.value])
                            break
                    else:
                        raise Exception(f"Undefined variable: {node.value}")

            # Lambda (create closure)
            elif node.type == 'lambda':
                closure = (node, self.env[-1].copy())
                self.stack.append(closure)

            # Function application
            elif node.type == 'gamma':
                func = self.stack.pop()
                arg = self.stack.pop()

                if callable(func):  # Built-in function
                    result = func(arg)
                    self.stack.append(result)
                elif isinstance(func, tuple) and func[0].type == 'lambda':  # Closure
                    lambda_node, env = func
                    var_node, body = lambda_node.children
                    new_env = env.copy()
                    new_env[var_node.value] = arg
                    self.env.append(new_env)
                    self.control.insert(0, body)
                    self.control.insert(0, ASTNode('env', value=len(self.env) - 1))
                elif isinstance(func, list) and isinstance(arg, int):  # Tuple indexing
                    if 1 <= arg <= len(func):
                        self.stack.append(func[arg - 1])  # RPAL uses 1-based indexing
                    else:
                        raise Exception(f"Index out of bounds: {arg}")
                else:
                    raise Exception(f"Invalid function application: {func}")

            # Tuple creation
            elif node.type == 'tau':
                elements = []
                for child in node.children:
                    self.control.insert(0, child)
                    self.evaluate()  # Evaluate child
                    elements.append(self.stack.pop())
                self.stack.append(elements)

            # Y combinator for recursion
            elif node.type == 'Y':
                func = self.stack.pop()
                if isinstance(func, tuple) and func[0].type == 'lambda':
                    lambda_node, env = func
                    var_node, body = lambda_node.children
                    # Create recursive closure
                    new_env = env.copy()
                    recursive_closure = (lambda_node, new_env)
                    new_env[var_node.value] = recursive_closure
                    self.stack.append(recursive_closure)
                else:
                    raise Exception("Y combinator expects a lambda")

            # Conditional
            elif node.type == '->':
                condition = self.stack.pop()
                then_branch, else_branch = node.children[1], node.children[2]
                self.control.insert(0, then_branch if condition else else_branch)

            # Arithmetic operators
            elif node.type == '+':
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a + b)

            elif node.type == '-':
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a - b)

            elif node.type == '*':
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a * b)

            elif node.type == '/':
                b, a = self.stack.pop(), self.stack.pop()
                if b == 0:
                    raise Exception("Division by zero")
                self.stack.append(a // b)

            # Comparison operators
            elif node.type == 'eq':
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(1 if a == b else 0)

            elif node.type == 'ne':
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(1 if a != b else 0)

            elif node.type == 'ls':
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(1 if a < b else 0)

            elif node.type == 'le':
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(1 if a <= b else 0)

            elif node.type == 'gr':
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(1 if a > b else 0)

            elif node.type == 'ge':
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(1 if a >= b else 0)

            # Logical operators
            elif node.type == 'and':
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(1 if a and b else 0)

            elif node.type == 'or':
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(1 if a or b else 0)

            elif node.type == 'not':
                a = self.stack.pop()
                self.stack.append(0 if a else 1)

            # Environment management
            elif node.type == 'env':
                while len(self.env) > node.value + 1:
                    self.env.pop()

            # Default: Push children to control stack
            else:
                for child in reversed(node.children):
                    self.control.insert(0, child)

        return self.stack[-1] if self.stack else None