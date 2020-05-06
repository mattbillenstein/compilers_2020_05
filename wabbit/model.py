from dataclasses import dataclass
from typing import Union, Optional, List


class Node:
    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"


class Statement(Node):
    pass


@dataclass
class Statements(Node):
    statements: List[Statement]


@dataclass
class Expression(Statement):
    pass


@dataclass
class Block(Expression):
    statements: Statements


@dataclass
class Integer(Expression):
    value: int


@dataclass
class Float(Expression):
    value: float


@dataclass
class Bool(Expression):
    value: bool


@dataclass
class Char(Expression):
    value: str


@dataclass
class Name(Expression):
    name: str


@dataclass
class UnaryOp(Expression):
    op: str
    right: Expression


@dataclass
class BinOp(Expression):
    op: str
    left: Expression
    right: Expression


@dataclass
class ConstDef(Statement):
    name: str
    type: Optional[str]
    value: Union[int, float]


@dataclass
class VarDef(Statement):
    name: str
    type: Optional[str]
    value: Optional[Expression]


@dataclass
class Assign(Statement):
    location: Name
    value: Expression


@dataclass
class Print(Statement):
    expression: Expression


@dataclass
class If(Statement):
    test: Expression
    then: Statements
    else_: Statements


@dataclass
class While(Statement):
    test: Expression
    then: Statements
