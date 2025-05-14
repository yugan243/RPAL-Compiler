from parser import ASTNode
class Standardizer:
    def standardize(self, ast):
        if not ast:
            return None
        if ast.type == 'let':
            expr, body = ast.children
            if body.type == 'where':
                where_expr = body.children[0]
                return ASTNode('gamma', children=[
                    ASTNode('lambda', children=[expr, self.standardize(body)]),
                    self.standardize(where_expr)
                ])
            return ASTNode('gamma', children=[
                ASTNode('lambda', children=[expr, self.standardize(body)]),
                self.standardize(expr)
            ])
        return ASTNode(ast.type, ast.value, [self.standardize(child) for child in ast.children])