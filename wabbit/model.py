from dataclasses import dataclass
from typing import Any, Union, Optional, List


class Statement:
    terminator = ";"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"

    @property
    def tokens(self) -> List[str]:
        raise NotImplementedError

    def to_source(self) -> str:
        return " ".join(tok for tok in self.tokens if tok is not None)

@dataclass
class Statements:
    statements: List[Statement]

    def to_source(self, level=0) -> str:
        indent = " " * 4 * level
        return "\n".join(indent + stmnt.to_source() + stmnt.terminator for stmnt in self.statements)


@dataclass
class Expression(Statement):
    pass


@dataclass
class Integer(Expression):
    value: int

    @property
    def tokens(self):
        return [str(self.value)]


@dataclass
class Float(Expression):
    value: float

    @property
    def tokens(self):
        return [str(self.value)]


@dataclass
class Name(Expression):
    name: str

    @property
    def tokens(self):
        return [self.name]


@dataclass
class UnaryOp(Expression):
    op: str
    right: Any

    @property
    def tokens(self):
        return [self.op, *self.right.tokens]


@dataclass
class BinOp(Expression):
    op: str
    left: Any
    right: Any

    @property
    def tokens(self):
        return [*self.left.tokens, self.op, *self.right.tokens]


@dataclass
class ConstDef(Statement):
    name: str
    type: Optional[str]
    value: Union[int, float]

    @property
    def tokens(self):
        return ["const", self.name, "=", self.type, str(self.value)]


@dataclass
class VarDef(Statement):
    name: str
    type: str
    value: Optional[Any]

    @property
    def tokens(self):
        tokens = ["var", self.name, self.type]
        if self.value is not None:
            tokens.extend(["=", str(self.value)])
        return tokens


@dataclass
class Assign(Statement):
    location: Any
    value: Any

    @property
    def tokens(self):
        return [self.location, "=", *self.value.tokens]


@dataclass
class Print(Statement):
    expression: Any

    @property
    def tokens(self):
        return ["print", *self.expression.tokens]


@dataclass
class If(Statement):
    test: Any
    then: Statements
    else_: Statements

    terminator = ""

    def to_source(self):
        # TODO: indentation
        return f"""\
if {self.test.to_source()} {{
{self.then.to_source(level=1)}
}} else {{
{self.else_.to_source(level=1)}
}}
"""


@dataclass
class While(Statement):
    test: Any
    then: Statements

    terminator = ""

    def to_source(self):
        # TODO: indentation
        return f"""\
while {self.test.to_source()} {{
{self.then.to_source(level=1)}
}}
"""


def to_source(program):
    return Statements(program or []).to_source()
