NoneType = type(None)

class SourceVisitor:
    def visit(self, node):
        m = getattr(self, f'visit_{node.__class__.__name__}')
        return m(node)

    def visit_Integer(self, node):
        return f'{node.value}'

    def visit_Float(self, node):
        return f'{node.value}'

    def visit_BinOp(self, node):
        return f'{self.visit(node.left)} {node.op} {self.visit(node.right)}'

    def visit_UnaOp(self, node):
        return f'{node.op}{self.visit(node.arg)}'

    def visit_Block(self, node):
        L = []
        for stmt in node.statements:
            s = self.visit(stmt) + ('' if stmt.is_statement else ';')
            # hack, split lines to add indent, then rejoin them...
            lines = [node.indent + _ for _ in s.split('\n') if _.strip()]
            s = '\n'.join(lines)
            L.append(s)
        return '\n'.join(L) + '\n'

    def visit_Print(self, node):
        return f'print {self.visit(node.arg)}'

    def visit_Const(self, node):
        type = f' {node.type}' if node.type is not None else ''
        return f'const {self.visit(node.loc)}{type} = {self.visit(node.arg)}'

    def visit_Var(self, node):
        arg = f' = {self.visit(node.arg)}' if node.arg is not None else ''
        type = f' {node.type}' if node.type is not None else ''
        return f'var {self.visit(node.loc)}{type}{arg}'

    def visit_Assign(self, node):
        return f'{self.visit(node.loc)} = {self.visit(node.arg)}'

    def visit_If(self, node):
        els = f' else {{\n{self.visit(node.eblock)}}}' if node.eblock is not None else ''
        return f'if {self.visit(node.cond)} {{\n{self.visit(node.block)}}}{els}'

    def visit_While(self, node):
        return f'while {self.visit(node.cond)} {{\n{self.visit(node.block)}}}'

    def visit_Compound(self, node):
        s = '; '.join(self.visit(_) for _ in node.statements) + ';'
        return f'{{ {s} }}'

    def visit_Name(self, node):
        return node.name


def to_source(node):
    return SourceVisitor().visit(node)
