from dataclasses import dataclass
from typing import Optional

from utils import print_source, print_diff
from .format_source import format_source
from .model import (  # noqa
    Assign,
    BinOp,
    Block,
    Bool,
    Char,
    ConstDef,
    Expression,
    Float,
    If,
    Integer,
    Location,
    Name,
    Print,
    UnaryOp,
    VarDef,
    While,
    Statement,
    Statements,
)
from .tokenize import tokenize, Token, TokenStream

blue = lambda s: __import__("clint").textui.colored.blue(s, always=True, bold=True)  # noqa
green = lambda s: __import__("clint").textui.colored.green(s, always=True, bold=True)  # noqa


@dataclass
class BaseParser:
    tokens: TokenStream
    lookahead: Optional[Token] = None

    def peek(self):
        if self.lookahead is None:
            self.lookahead = next(self.tokens)
        return self.lookahead

    def expect(self, type_) -> Token:
        print(blue(f"expect({type_}) next = {self.peek()}"))
        tok = self.peek()
        assert tok.type_ == type_, f"Expected {type_}, got {tok}"

        print(green(f"    -> {tok}"))
        self.lookahead = None
        return tok

    def accept(self, type_) -> Optional[Token]:
        print(blue(f"accept({type_}) next = {self.peek()}"))
        tok = self.peek()
        if tok.type_ == type_:
            print(green(f"    -> {tok}"))
            self.lookahead = None
            return tok
        print(blue(f"    -> reject"))
        return None


class Parser(BaseParser):
    # program : statements EOF
    def program(self) -> Statements:
        statements = self.statements()
        self.expect("EOF")  # TODO
        node = statements

        print(green(f"Parsed {node}"))
        return node

    # statements : { statement }
    #
    def statements(self) -> Statements:
        statements = []
        while True:
            try:
                statements.append(self.statement())
            except StopIteration:  # TODO: avoid catching the wrong StopIteration
                return Statements(statements)

    # statement : print_statement
    #           | assignment_statement
    #           | variable_definition
    #           | const_definition
    #           | if_statement
    #           | while_statement
    #           | break_statement
    #           | continue_statement
    #           | expr
    #

    def statement(self) -> Statement:

        node = self.print() or self.assign() or self.vardef() or self.constdef()

        assert node

        print(green(f"Parsed {node}"))
        return node

    # print_statement : PRINT expr SEMICOLON
    #
    def print(self) -> Optional[Statement]:
        print(blue(f"print(): next = {self.peek()}"))

        if self.accept("PRINT"):
            self.lookahead = None
        else:
            return None

        expression = self.expression()
        self.expect("SEMICOLON")
        node = Print(expression)

        print(green(f"    Parsed {node}"))
        return node

    # assignment_statement : LOCATION = EXPRESSION SEMICOLON
    #
    def assign(self) -> Optional[Statement]:
        print(blue(f"assign(): next = {self.peek()}"))

        if tok := self.accept("NAME"):  # TODO: location
            location = Location(tok.token)
            self.lookahead = None
        else:
            return None

        self.expect("ASSIGN")

        expression = self.expression()
        self.expect("SEMICOLON")
        node = Assign(location, expression)

        print(green(f"    Parsed {node}"))
        return node

    # variable_definition : VAR NAME [ type ] ASSIGN expr SEMI
    #                     | VAR NAME type [ ASSIGN expr ] SEMI
    def vardef(self):
        print(blue(f"vardef(): next = {self.peek()}"))

        if self.accept("VAR"):
            self.lookahead = None
        else:
            return None

        name = Name(self.expect("NAME").token)

        type_: Optional[str]
        if tok := self.accept("TYPE"):
            type_ = tok.token
            self.lookahead = None
        else:
            type_ = None

        self.expect("ASSIGN")

        value = (
            self.expression()
        )  # TODO: value might be missing, in which case type must be present

        self.expect("SEMICOLON")
        node = VarDef(name, type_, value)

        print(green(f"    Parsed {node}"))
        return node

    # const_definition : CONST NAME [ type ] ASSIGN expr SEMI
    def constdef(self):
        print(blue(f"constdef(): next = {self.peek()}"))

        if self.accept("CONST"):
            self.lookahead = None
        else:
            return None

        name = Name(self.expect("NAME").token)

        if tok := self.accept("TYPE"):
            type_ = tok.token
            self.lookahead = None
        else:
            type_ = None

        self.expect("ASSIGN")

        value = self.expression()

        self.expect("SEMICOLON")
        node = ConstDef(name, type_, value)

        print(green(f"    Parsed {node}"))
        return node

    def expression(self) -> Expression:
        print(blue(f"expression(): next = {self.peek()}"))

        tok = self.peek()
        node: Expression  # TODO: why?
        if tok.type_ == "INTEGER":
            node = Integer(int(tok.token))
        elif tok.type_ == "FLOAT":
            node = Float(float(tok.token))
        elif tok.type_ == "BOOL":
            node = Bool(bool(tok.token))
        elif tok.type_ == "CHAR":
            node = Char(tok.token)
        else:
            raise RuntimeError(f"Error parsing expression: {tok}")

        print(green(f"    Parsed {node}"))
        self.lookahead = None
        return node


# Top-level function that runs everything
def parse_source(source):
    print_source(source)

    # Tokenize
    tokens = list(tokenize(source))
    for tok in tokens:
        print(tok)
    print()
    token_stream = (tok for tok in tokens)

    # Parse

    model = Parser(token_stream).statements()

    print(model)

    # Format
    transpiled = format_source(model)
    print_diff(source, transpiled)

    return model


# Example of a main program
def parse_file(filename):
    with open(filename) as file:
        text = file.read()
    return parse_source(text)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise SystemExit("Usage: wabbit.parse filename")
    parse_file(sys.argv[1])
