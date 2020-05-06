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
    def interpret(self, node: Node, env: ChainMap, **kwargs):
        method_name = "interpret_" + node.__class__.__name__
        return getattr(self, method_name)(node, env, **kwargs)

    @typechecked
    def interpret_Float(self, node: Float, env):
        return node.value

    @typechecked
    def interpret_Integer(self, node: Integer, env):
        return node.value

    @typechecked
    def interpret_Name(self, node: Name, env):
        return env[node.name]

    @typechecked
    def interpret_UnaryOp(self, node: UnaryOp, env):
        right_val = self.interpret(node.right, env)
        return UNARY_OPERATORS[node.op](right_val)

    @typechecked
    def interpret_BinOp(self, node: BinOp, env):
        left_val = self.interpret(node.left, env)
        right_val = self.interpret(node.right, env)
        return OPERATORS[node.op](left_val, right_val)

    @typechecked
    def interpret_ConstDef(self, node: ConstDef, env):
        env[node.name] = node.value

    @typechecked
    def interpret_VarDef(self, node: VarDef, env):
        if node.value is not None:
            env[node.name] = self.interpret(node.value, env)

    @typechecked
    def interpret_Assign(self, node: Assign, env):
        # TODO
        env[node.location.name] = self.interpret(node.value, env)

    @typechecked
    def interpret_Print(self, node: Print, env):
        sys.stdout.write(str(self.interpret(node.expression, env)) + "\n")

    @typechecked
    def interpret_If(self, node: If, env):
        if self.interpret(node.test, env):
            return self.interpret(node.then, env)
        else:
            return self.interpret(node.else_, env)

    @typechecked
    def interpret_While(self, node: While, env):
        while self.interpret(node.test, env):
            self.interpret(node.then, env)

    @typechecked
    def interpret_Statements(self, node: Statements, env):
        for statement in node.statements:
            self.interpret(statement, env)

    @typechecked
    def interpret_Block(self, node: Block, env):
        env = env.new_child()
        for statement in node.statements.statements:
            val = self.interpret(statement, env)
        return val


@typechecked
def interpret_program(node: Statements):
    env: ChainMap = ChainMap()
    return Interpreter().interpret(node, env)
