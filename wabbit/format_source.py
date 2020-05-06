from typeguard import typechecked

from wabbit.model import (
    Assign,
    BinOp,
    Block,
    Bool,
    Char,
    ConstDef,
    Float,
    If,
    Integer,
    Name,
    Print,
    Statements,
    UnaryOp,
    VarDef,
    While,
)


class SourceFormatter:
    """
    Format model as source code.
    """

    @typechecked
    def visit(self, node, **kwargs) -> str:
        method_name = "visit_" + node.__class__.__name__
        return getattr(self, method_name)(node, **kwargs)

    @typechecked
    def visit_Float(self, node: Float) -> str:
        return str(node.value)

    @typechecked
    def visit_Integer(self, node: Integer) -> str:
        return str(node.value)

    @typechecked
    def visit_Char(self, node: Char) -> str:
        return f"'{node.value}'"

    @typechecked
    def visit_Bool(self, node: Bool) -> str:
        return {True: "true", False: "false"}[node.value]

    @typechecked
    def visit_Name(self, node: Name) -> str:
        return node.value

    @typechecked
    def visit_Location(self, node: Name) -> str:
        return self.visit_Name(node)

    @typechecked
    def visit_UnaryOp(self, node: UnaryOp) -> str:
        return node.op + self.visit(node.right)

    @typechecked
    def visit_BinOp(self, node: BinOp) -> str:
        return " ".join([self.visit(node.left), node.op, self.visit(node.right)])

    @typechecked
    def visit_ConstDef(self, node: ConstDef) -> str:
        tokens = (
            ["const", node.name.value, "="]
            + ([node.type] if node.type else [])
            + [self.visit(node.value)]
        )
        return " ".join(tokens)

    @typechecked
    def visit_VarDef(self, node: VarDef) -> str:
        tokens = ["var", node.name.value]
        if node.type is not None:
            tokens.append(node.type)
        if node.value is not None:
            tokens.extend(["=", self.visit(node.value)])
        return " ".join(tokens)

    @typechecked
    def visit_Assign(self, node: Assign) -> str:
        return " ".join([self.visit(node.location), "=", self.visit(node.value)])

    @typechecked
    def visit_Print(self, node: Print) -> str:
        return " ".join(["print", self.visit(node.expression)])

    @typechecked
    def visit_If(self, node: If) -> str:
        # TODO: hard-coded indent=1
        return """\
if %s {
%s
} else {
%s
}
""" % (
            self.visit(node.test),
            self.visit(node.then, level=1),
            self.visit(node.else_, level=1),
        )

    @typechecked
    def visit_While(self, node: While) -> str:
        # TODO: hard-coded indent=1
        return """\
while %s {
%s
}
""" % (
            self.visit(node.test),
            self.visit(node.then, level=1),
        )

    @typechecked
    def visit_Statements(self, node: Statements, level=0) -> str:
        indent = " " * 4 * level
        return "\n".join(indent + self.visit(stmnt) + ";" for stmnt in node.statements)

    @typechecked
    def visit_Block(self, node: Block, level=0) -> str:
        return """{
%s
}
""" % self.visit_Statements(
            node.statements, level=level + 1
        )


@typechecked
def format_source(node: Statements) -> str:
    return SourceFormatter().visit(node, level=0)
