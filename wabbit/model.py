from dataclasses import dataclass
from typing import Any


@dataclass
class Integer:
    value: int

    def __repr__(self):
        return f"Integer({self.value})"


@dataclass
class Float:
    value: float

    def __repr__(self):
        return f"Float({self.value})"


@dataclass
class UnaryOp:
    op: str
    right: Any

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.right})"


@dataclass
class BinOp:
    op: str
    left: Any
    right: Any

    def __repr__(self):
        return f"BinOp({self.op}, {self.left}, {self.right})"


@dataclass
class PrintStatement:
    expression: Any

    def __repr__(self):
        return f"PrintStatement({self.expression})"


def print_source(program):
    for statement in program or []:
        print(to_source(statement))


def to_source(node):
    if isinstance(node, (Integer, Float)):
        return repr(node.value)
    elif isinstance(node, UnaryOp):
        return f"{node.op}{to_source(node.right)}"
    elif isinstance(node, BinOp):
        return f"{to_source(node.left)} {node.op} {to_source(node.right)}"
    elif isinstance(node, PrintStatement):
        return f"Print({to_source(node.expression)})"
    else:
        raise RuntimeError(f"Can't convert {node} to source")
