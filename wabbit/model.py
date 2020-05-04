from dataclasses import dataclass
from typing import Any, Union


class Node:
    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"


@dataclass
class Integer(Node):
    value: int


@dataclass
class Float(Node):
    value: float


@dataclass
class Name(Node):
    name: str


@dataclass
class UnaryOp(Node):
    op: str
    right: Any


@dataclass
class BinOp(Node):
    op: str
    left: Any
    right: Any


@dataclass
class ConstDef(Node):
    name: str
    value: Union[int, float]
    type: str = None


@dataclass
class VarDef(Node):
    name: str
    type: str
    value: Any = None


@dataclass
class Assignment(Node):
    location: Any
    value: Any


@dataclass
class Print(Node):
    expression: Any


@dataclass
class If(Node):
    tst: Any
    thn: Any
    els: Any


def to_source(program):
    return "\n".join(_to_source(stmnt) + ";" for stmnt in program or [])


def _to_source(node):

    if isinstance(node, (Integer, Float)):
        return str(node.value)

    elif isinstance(node, UnaryOp):
        return "".join([node.op, _to_source(node.right)])

    elif isinstance(node, BinOp):
        return " ".join([_to_source(node.left), node.op, _to_source(node.right)])

    elif isinstance(node, Name):
        return node.name

    elif isinstance(node, ConstDef):
        return " ".join(["const", node.name if node.name is not None else "", str(node.value)])

    elif isinstance(node, VarDef):
        tokens = ["var", node.name, node.type]
        if node.value is not None:
            tokens.extend(["=", str(node.value)])
        return " ".join(tokens)

    elif isinstance(node, Assignment):
        return " ".join([node.location, "=", _to_source(node.value)])

    elif isinstance(node, If):
        return " ".join(
            [
                "if",
                _to_source(node.tst),
                "{",
                _to_source(node.thn),
                "}",
                "{",
                _to_source(node.els),
                "}",
            ]
        )

    elif isinstance(node, Print):
        return " ".join(["print", _to_source(node.expression)])

    else:
        raise RuntimeError(f"Can't convert {node} to source")
