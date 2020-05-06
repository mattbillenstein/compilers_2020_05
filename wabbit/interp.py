from collections import ChainMap
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
    @typechecked
    def visit(self, node: Node, env: ChainMap, **kwargs):
        method_name = "visit_" + node.__class__.__name__
        return getattr(self, method_name)(node, env, **kwargs)

    @typechecked
    def visit_Float(self, node: Float, env):
        return node.value

    @typechecked
    def visit_Integer(self, node: Integer, env):
        return node.value

    @typechecked
    def visit_Name(self, node: Name, env):
        return self.env[node.name]

    @typechecked
    def visit_UnaryOp(self, node: UnaryOp, env):
        right_val = self.visit(node.right)
        return UNARY_OPERATORS[node.op](right_val)

    @typechecked
    def visit_BinOp(self, node: BinOp, env):
        left_val = self.visit(node.left)
        right_val = self.visit(node.right)
        return OPERATORS[node.op](left_val, right_val)

    @typechecked
    def visit_ConstDef(self, node: ConstDef, env):
        self.env[node.name] = node.value

    @typechecked
    def visit_VarDef(self, node: VarDef, env):
        if node.value is not None:
            self.env[node.name] = self.visit(node.value)

    @typechecked
    def visit_Assign(self, node: Assign, env):
        # TODO
        self.env[node.location] = self.visit(node.value)

    @typechecked
    def visit_Print(self, node: Print, env):
        sys.stdout.write(str(self.visit(node.expression)) + "\n")

    @typechecked
    def visit_If(self, node: If, env):
        if self.visit(node.test):
            return self.visit(node.then)
        else:
            return self.visit(node.else_)

    @typechecked
    def visit_While(self, node: While, env):
        while self.visit(node.test):
            self.visit(node.then)

    @typechecked
    def visit_Statements(self, node: Statements, env):
        for statement in node.statements:
            self.visit(statement)

    @typechecked
    def visit_Block(self, node: Block, env):
        for statement in node.statements.statements:
            val = self.visit(statement)
        return val


@typechecked
def interpret_program(node: Statements):
    env: ChainMap = ChainMap()
    return Interpreter().visit(node, env)
