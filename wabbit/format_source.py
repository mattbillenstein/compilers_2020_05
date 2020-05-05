class SourceFormatter:
    """
    Format model as source code.
    """

    def visit(self, node, **kwargs) -> str:
        method_name = "visit_" + node.__class__.__name__
        return getattr(self, method_name)(node, **kwargs)

    def visit_Statements(self, node, level=0):
        indent = " " * 4 * level
        return "\n".join(indent + self.visit(stmnt) + ";" for stmnt in node.statements)

    def visit_Float(self, node):
        return str(node.value)

    def visit_Integer(self, node):
        return str(node.value)

    def visit_Name(self, node):
        return node.name

    def visit_UnaryOp(self, node):
        return node.op + self.visit(node.right)

    def visit_BinOp(self, node):
        return " ".join([self.visit(node.left), node.op, self.visit(node.right)])

    def visit_ConstDef(self, node):
        tokens = ["const", node.name, "="] + (node.type or []) + [str(node.value)]
        return " ".join(tokens)

    def visit_VarDef(self, node):
        tokens = ["var", node.name, node.type]
        if node.value is not None:
            tokens.extend(["=", str(node.value)])
        return " ".join(tokens)

    def visit_Assign(self, node):
        return " ".join([node.location, "=", self.visit(node.value)])

    def visit_Print(self, node):
        return " ".join(["print", self.visit(node.expression)])

    def visit_If(self, node):
        # TODO: hard-coded indent=1
        return f"""\
if {self.visit(node.test)} {{
{self.visit(node.then, level=1)}
}} else {{
{self.visit(node.else_, level=1)}
}}
"""
    def visit_While(self, node):
        # TODO: hard-coded indent=1
        return f"""\
while {self.visit(node.test)} {{
{self.visit(node.then, level=1)}
}}
"""

def format_source(node):
    return SourceFormatter().visit(node, level=0)
