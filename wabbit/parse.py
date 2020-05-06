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

    def expect(self, type_):
        print(blue(f"expect({type_}) next = {self.peek()}"))
        tok = self.peek()
        assert tok.type_ == type_, f"Expected {type_}, got {tok}"

        print(green(f"    -> {tok}"))
        self.lookahead = None
        return tok

    def accept(self, type_):
        print(blue(f"accept({type_}) next = {self.peek()}"))
        tok = self.peek()
        if tok.type_ == type_:
            print(green(f"    -> {tok}"))
            self.lookahead = None
            return tok


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

        node = self.print_statement()

        print(green(f"Parsed {node}"))
        return node

    # print_statement : PRINT expr SEMICOLON
    #
    def print_statement(self) -> Statement:
        print(blue(f"print_statement(): next = {self.peek()}"))
        self.expect("PRINT")
        expression = self.expression()
        self.expect("SEMICOLON")
        node = Print(expression)

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
