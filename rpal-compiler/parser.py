from lexer import tokenize_file

class ASTNode:
    def __init__(self,type,value = None):
        self.type = type
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self):
        return f"ASTNode({self.value})"