from dataclasses import dataclass
from typing import Any, Union


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
class Name:
    name: str

    def __repr__(self):
        return f"Name({self.name})"


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
class ConstDeclaration:
    name: str
    value: Union[int, float]
    type: str = None

    def __repr__(self):
        return f"ConstDeclaration({self.name}, {self.type}, {self.value})"


@dataclass
class VarDeclaration:
    name: str
    type: str
    value: Any = None

    def __repr__(self):
        return f"VarDeclaration({self.name}, {self.type}, {self.value})"


@dataclass
class Assignment:
    name: str
    value: Any

    def __repr__(self):
        return f"Assignment({self.name}, {self.value})"


@dataclass
class PrintStatement:
    expression: Any

    def __repr__(self):
        return f"PrintStatement({self.expression})"


def print_source(program):
    for statement in program or []:
        print(f"{_to_source(statement)};")


def _to_source(node):

    if isinstance(node, (Integer, Float)):
        return repr(node.value)

    elif isinstance(node, UnaryOp):
        return f"{node.op}{_to_source(node.right)}"

    elif isinstance(node, BinOp):
        return f"{_to_source(node.left)} {node.op} {_to_source(node.right)}"

    elif isinstance(node, Name):
        return f"{node.name}"

    elif isinstance(node, ConstDeclaration):
        return f"const {node.name} {node.type or ''} = {node.value}"

    elif isinstance(node, VarDeclaration):
        return f"var {node.name} {node.type}" + (f"= {node.value}" if node.value else "")

    elif isinstance(node, Assignment):
        return f"{node.name} = {_to_source(node.value)}"

    elif isinstance(node, PrintStatement):
        return f"print {_to_source(node.expression)}"

    else:
        raise RuntimeError(f"Can't convert {node} to source")
