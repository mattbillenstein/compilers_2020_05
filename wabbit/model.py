import dataclasses
from functools import partial
from typing import Union, Optional, List


# Hashable instances
dataclass = partial(dataclasses.dataclass, eq=False)


class Node:
    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)  # type: ignore
        from .parse import Parser

        Parser.line_num_map[self] = Parser.line_num
        return self


class Statement(Node):
    pass


@dataclass
class Statements(Node):
    statements: List[Statement]


@dataclass
class Expression(Statement):
    pass


@dataclass
class ParenthesizedExpression(Statement):
    expression: Expression


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
    value: str


@dataclass
class Location(Name):
    pass


@dataclass
class UnaryOp(Expression):
    op: str
    right: Expression


@dataclass
class BinOp(Expression):
    op: str
    left: Expression
    right: Expression


Literal = Union[Bool, Char, Float, Integer]


@dataclass
class ConstDef(Statement):
    name: Name
    type: Optional[str]
    value: Literal


@dataclass
class VarDef(Statement):
    name: Name
    type: Optional[str]
    value: Optional[Expression]


@dataclass
class Assign(Statement):
    location: Location
    value: Expression


@dataclass
class Print(Statement):
    expression: Expression


@dataclass
class If(Statement):
    test: Expression
    then: Statements
    else_: Optional[Statements]


@dataclass
class While(Statement):
    test: Expression
    then: Statements
