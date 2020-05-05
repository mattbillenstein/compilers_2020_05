from dataclasses import dataclass
import operator
import sys

from typeguard import typechecked

from wabbit.model import (
    Assign,
    BinOp,
    Block,
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

OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "<": operator.lt,
    ">": operator.gt,
    ">=": operator.ge,
    "<=": operator.le,
}

UNARY_OPERATORS = {
    "-": lambda x: -x,
}


@dataclass
class Interpreter:
    env: dict

    @typechecked
    def visit(self, node: Node, **kwargs):
        method_name = "visit_" + node.__class__.__name__
        return getattr(self, method_name)(node, **kwargs)

    @typechecked
    def visit_Statements(self, node: Statements):
        for statement in node.statements:
            self.visit(statement)

    @typechecked
    def visit_Block(self, node: Block):
        for statement in node.statements.statements:
            val = self.visit(statement)
        return val

    @typechecked
    def visit_Float(self, node: Float):
        return node.value

    @typechecked
    def visit_Integer(self, node: Integer):
        return node.value

    @typechecked
    def visit_Name(self, node: Name):
        return self.env[node.name]

    @typechecked
    def visit_UnaryOp(self, node: UnaryOp):
        right_val = self.visit(node.right)
        return UNARY_OPERATORS[node.op](right_val)

    @typechecked
    def visit_BinOp(self, node: BinOp):
        left_val = self.visit(node.left)
        right_val = self.visit(node.right)
        return OPERATORS[node.op](left_val, right_val)

    @typechecked
    def visit_ConstDef(self, node: ConstDef):
        self.env[node.name] = node.value

    @typechecked
    def visit_VarDef(self, node: VarDef):
        self.env[node.name] = node.value

    @typechecked
    def visit_Assign(self, node: Assign):
        # TODO
        self.env[node.location] = node.value

    @typechecked
    def visit_Print(self, node: Print):
        sys.stdout.write(str(self.visit(node.expression)) + "\n")

    @typechecked
    def visit_If(self, node: If):
        if self.visit(node.test):
            return self.visit(node.then)
        else:
            return self.visit(node.else_)

    @typechecked
    def visit_While(self, node: While):
        if self.visit(node.test):
            return self.visit(node.then)


@typechecked
def interpret_program(node: Statements):
    return Interpreter({}).visit(node)
