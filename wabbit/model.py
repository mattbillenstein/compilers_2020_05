from dataclasses import dataclass
from typing import Any, Union, Optional


class Node:
    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"

    @property
    def tokens(self):
        raise NotImplementedError


@dataclass
class Integer(Node):
    value: int

    @property
    def tokens(self):
        return [str(self.value)]


@dataclass
class Float(Node):
    value: float

    @property
    def tokens(self):
        return [str(self.value)]


@dataclass
class Name(Node):
    name: str

    @property
    def tokens(self):
        return [self.name]


@dataclass
class UnaryOp(Node):
    op: str
    right: Any

    @property
    def tokens(self):
        return [self.op, *self.right.tokens]


@dataclass
class BinOp(Node):
    op: str
    left: Any
    right: Any

    @property
    def tokens(self):
        return [*self.left.tokens, self.op, *self.right.tokens]


@dataclass
class ConstDef(Node):
    name: str
    value: Union[int, float]
    type: Optional[str] = None

    @property
    def tokens(self):
        return ["const", self.name if self.name is not None else "", str(self.value)]


@dataclass
class VarDef(Node):
    name: str
    type: str
    value: Any = None

    @property
    def tokens(self):
        tokens = ["var", self.name, self.type]
        if self.value is not None:
            tokens.extend(["=", str(self.value)])
        return tokens


@dataclass
class Assignment(Node):
    location: Any
    value: Any

    @property
    def tokens(self):
        return [self.location, "=", *self.value.tokens]


@dataclass
class Print(Node):
    expression: Any

    @property
    def tokens(self):
        return ["print", *self.expression.tokens]


@dataclass
class If(Node):
    tst: Any
    thn: Any
    els: Any

    @property
    def tokens(self):
        return [
            "if",
            *self.tst.tokens,
            "{",
            *self.thn.tokens,
            "}",
            "{",
            *self.els.tokens,
            "}",
        ]


def to_source(program):
    return "\n".join(" ".join(node.tokens) + ";" for node in program or [])
