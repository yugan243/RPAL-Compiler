class Node:
    def __init__(self, type, value=None, children=None):
        self.type = type
        self.value = value
        self.children = children or []

    def __str__(self):
        return f"{self.type}: {self.value}" if self.value else self.type

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None

    def advance(self):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def parse(self):
        return self.parse_expression()

    def parse_expression(self):
        if not self.current_token:
            return None
        if self.current_token[1] == 'let':
            return self.parse_let()
        # Add more cases for other constructs (e.g., gamma, tau)
        return self.parse_primary()

    def parse_let(self):
        self.advance()  # Consume 'let'
        expr = self.parse_expression()
        if self.current_token and self.current_token[1] == 'in':
            self.advance()
            body = self.parse_expression()
            return Node('let', children=[expr, body])
        elif self.current_token and self.current_token[1] == 'where':
            self.advance()
            where_expr = self.parse_expression()
            return Node('let', children=[expr, Node('where', children=[where_expr])])
        return expr

    def parse_primary(self):
        token = self.current_token
        if not token:
            return None
        if token[0] == 'IDENTIFIER':
            self.advance()
            return Node('ID', token[1])
        elif token[0] == 'INTEGER':
            self.advance()
            return Node('INT', token[1])
        elif token[0] == 'KEYWORD' and token[1] in ['gamma', 'tau', 'rec']:
            self.advance()
            children = []
            while self.current_token and self.current_token[1] != 'in':
                children.append(self.parse_expression())
            return Node(token[1], children=children)
        # Add more cases as per grammar
        self.advance()
        return None

    def print_ast(self, node, indent=0):
        if not node:
            return
        print('  ' * indent + str(node))
        for child in node.children:
            self.print_ast(child, indent + 1)