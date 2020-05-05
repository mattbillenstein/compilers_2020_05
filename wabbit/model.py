from dataclasses import dataclass
from typing import Any, Union, Optional, List


class Statement:
    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"


@dataclass
class Statements:
    statements: List[Statement]


@dataclass
class Expression(Statement):
    pass


@dataclass
class Integer(Expression):
    value: int


@dataclass
class Float(Expression):
    value: float


@dataclass
class Name(Expression):
    name: str


@dataclass
class UnaryOp(Expression):
    op: str
    right: Any


@dataclass
class BinOp(Expression):
    op: str
    left: Any
    right: Any


@dataclass
class ConstDef(Statement):
    name: str
    type: Optional[str]
    value: Union[int, float]


@dataclass
class VarDef(Statement):
    name: str
    type: Optional[str]
    value: Optional[Any]


@dataclass
class Assign(Statement):
    location: Any
    value: Any


@dataclass
class Print(Statement):
    expression: Any


@dataclass
class If(Statement):
    test: Any
    then: Statements
    else_: Statements


@dataclass
class While(Statement):
    test: Any
    then: Statements
