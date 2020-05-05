from typeguard import typechecked

from wabbit.model import (
    Assign,
    BinOp,
    ConstDef,
    Float,
    If,
    Integer,
    Name,
    Node,
    Print,
    UnaryOp,
    VarDef,
    While,
    Statements,
)


class SyntaxChecker:
    """
    Format model as source code.
    """

    @typechecked
    def visit(self, node: Node, **kwargs):
        method_name = "visit_" + node.__class__.__name__
        method = getattr(self, method_name, None)
        if method:
            method(node, **kwargs)
        else:
            if hasattr(node, "left"):
                self.visit(node.left)  # type: ignore
            if hasattr(node, "right"):
                self.visit(node.right)  # type: ignore

    @typechecked
    def visit_VarDef(self, node: VarDef):
        assert node.type or node.value


@typechecked
def check_syntax(node: Statements):
    return SyntaxChecker().visit(node)
