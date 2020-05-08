import sys
from collections import ChainMap
from dataclasses import dataclass
import operator


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
    Node,
    ParenthesizedExpression,
    Print,
    Statements,
    UnaryOp,
    VarDef,
    While,
)


_DIV_OPERATORS = {
    (float, float): operator.truediv,
    (int, int): operator.floordiv,
}

OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": lambda x, y: _DIV_OPERATORS[type(x), type(y)](x, y),
    "<": operator.lt,
    ">": operator.gt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
    # TODO: these python operators operate bitwise, is this ok?
    "&&": operator.and_,
    "||": operator.or_,
}

UNARY_OPERATORS = {
    "-": operator.neg,
    "+": operator.pos,
    "!": operator.not_,
}


@dataclass
class Interpreter:
    def interpret(self, node: Node, env: ChainMap, **kwargs):
        method_name = "interpret_" + node.__class__.__name__
        return getattr(self, method_name)(node, env, **kwargs)

    def interpret_Bool(self, node: Bool, env) -> bool:
        return node.value

    def interpret_Char(self, node: Char, env) -> str:
        return node.value

    def interpret_Float(self, node: Float, env) -> float:
        return node.value

    def interpret_Integer(self, node: Integer, env) -> int:
        return node.value

    def interpret_Name(self, node: Name, env):
        return env[node.value]

    def interpret_UnaryOp(self, node: UnaryOp, env):
        right_val = self.interpret(node.right, env)
        return UNARY_OPERATORS[node.op](right_val)

    def interpret_BinOp(self, node: BinOp, env):
        left_val = self.interpret(node.left, env)
        right_val = self.interpret(node.right, env)
        return OPERATORS[node.op](left_val, right_val)

    def interpret_ParenthesizedExpression(self, node: ParenthesizedExpression, env):
        return self.interpret(node.expression, env)

    def interpret_ConstDef(self, node: ConstDef, env):
        env[node.left.value] = self.interpret(node.right, env)

    def interpret_VarDef(self, node: VarDef, env):
        if node.right is not None:
            env[node.left.value] = self.interpret(node.right, env)

    def interpret_Assign(self, node: Assign, env):
        value = node.left.value
        receiving_env = next((env for env in env.maps if value in env), env)
        receiving_env[value] = self.interpret(node.right, env)

    def interpret_Print(self, node: Print, env):
        value = self.interpret(node.expression, env)
        if isinstance(value, str):
            # Hack: bug in tokenizer
            if value == "\\n":
                value = "\n"
            sys.stdout.write(value)
        elif isinstance(value, float):
            sys.stdout.write(f"{value:.6f}\n")
        elif isinstance(value, bool):
            sys.stdout.write({True: "true", False: "false"}[value] + "\n")
        else:
            sys.stdout.write(f"{value}\n")
        sys.stdout.flush()

    def interpret_If(self, node: If, env):
        if self.interpret(node.test, env):
            return self.interpret(node.then, env)
        elif node.else_:
            return self.interpret(node.else_, env)

    def interpret_While(self, node: While, env):
        while self.interpret(node.test, env):
            self.interpret(node.then, env)

    def interpret_Statements(self, node: Statements, env):
        for statement in node.statements:
            self.interpret(statement, env)

    def interpret_Block(self, node: Block, env):
        env = env.new_child()
        for statement in node.statements.statements:
            val = self.interpret(statement, env)
        return val


def interpret_program(node: Statements):
    env: ChainMap = ChainMap()
    return Interpreter().interpret(node, env)


if __name__ == "__main__":
    from wabbit.parse import parse_source

    debug = False
    args = sys.argv[1:]
    if args[0] == "-d":
        debug = True
        args = args[1:]

    with open(args[0]) as fh:
        interpret_program(parse_source(fh.read(), debug))
