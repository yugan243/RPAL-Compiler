from parser import ASTNode

class CSEMachine:
    def __init__(self, st):
        self.control = [st]
        self.stack = []
        self.env = [{}]

    def evaluate(self):
        while self.control:
            node = self.control.pop(0)
            if node.type == 'INT':
                self.stack.append(int(node.value))
            elif node.type == 'ID':
                for env in self.env:
                    if node.value in env:
                        self.stack.append(env[node.value])
                        break
            elif node.type == 'gamma':
                func = self.stack.pop()
                arg = self.stack.pop()
                if isinstance(func, ASTNode) and func.type == 'lambda':
                    new_env = self.env[-1].copy()
                    new_env[func.children[0].value] = arg
                    self.env.append(new_env)
                    self.control.insert(0, func.children[1])
            elif node.type == '+':
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a + b)
        return self.stack[-1] if self.stack else None