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
    Literal,
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


# def print(*args):
#     pass


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

    def accept(self, *types_) -> Optional[Token]:
        # print(blue(f"accept({types_}) next = {self.peek()}"))
        try:
            tok = self.peek()
        except StopIteration:
            return None

        if tok.type_ in types_:
            print(green(f"    -> {tok}"))
            self.lookahead = None
            return tok
        # print(blue("    -> reject"))
        return None


class Parser(BaseParser):
    # program : statements EOF
    def program(self) -> Statements:
        statements = self.statements()
        self.expect("EOF")  # TODO
        node = statements

        print(green(f"parsed Program: {node}"))
        return node

    # statements : { statement }
    #
    def statements(self) -> Statements:
        statements = []
        while True:
            try:
                statement = self.statement()
            except StopIteration:  # TODO: ensure this is an appropriate StopIteration to catch
                break
            if not statement:
                break
            statements.append(statement)

        print(green(f"    parsed Statements: {statements}"))
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

    def statement(self) -> Optional[Statement]:
        print(blue(f"statement(): next = {self.peek()}"))

        statement = (
            self.print()
            or self.vardef()
            or self.constdef()
            or self.if_()
            or self.expression()
            or self.assign()
        )

        if statement:
            print(green(f"    parsed Statement: {statement}"))

            if self.accept("SEMICOLON"):  # ?
                self.lookahead = None

            return statement

    # if_statement : IF expr LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]
    def if_(self) -> Optional[Statement]:
        if not self.accept("IF"):
            return None

        self.lookahead = None
        assert (test := self.expression())
        assert (then := self.block())
        else_ = self._else()
        return If(test, then.statements, else_.statements if else_ else None)

    def _else(self) -> Optional[Block]:
        if not self.accept("ELSE"):
            return None
        self.lookahead = None
        assert (block := self.block())
        return block

    def while_(self) -> Optional[Statement]:
        if not self.accept("WHILE"):
            return None

        self.lookahead = None
        assert (test := self.expression())
        assert (then := self.block())
        return While(test, then.statements)

    def block(self) -> Optional[Block]:
        if not self.accept("LBRACE"):
            return None
        statements = self.statements()
        self.expect("RBRACE")
        return Block(statements)

    # print_statement : PRINT expr SEMICOLON
    #
    def print(self) -> Optional[Statement]:
        print(blue(f"print(): next = {self.peek()}"))

        if not self.accept("PRINT"):
            return None

        self.lookahead = None

        assert (expression := self.expression())
        self.expect("SEMICOLON")
        node = Print(expression)

        print(green(f"    parsed Print: {node}"))
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

        assert (expression := self.expression())
        self.expect("SEMICOLON")
        node = Assign(location, expression)

        print(green(f"    Parsed Assign: {node}"))
        return node

    # variable_definition : VAR NAME [ type ] ASSIGN expr SEMI
    #                     | VAR NAME type [ ASSIGN expr ] SEMI
    def vardef(self) -> Optional[VarDef]:
        print(blue(f"vardef(): next = {self.peek()}"))

        if not self.accept("VAR"):
            return None

        self.lookahead = None
        name = Name(self.expect("NAME").token)

        type_: Optional[str]
        if tok := self.accept("TYPE"):
            type_ = tok.token
            self.lookahead = None
        else:
            type_ = None

        if self.accept("ASSIGN"):
            self.lookahead = None
            assert (value := self.expression())
        else:
            value = None
            assert type_

        self.expect("SEMICOLON")
        node = VarDef(name, type_, value)

        print(green(f"    parsed VarDef {node}"))
        return node

    # const_definition : CONST NAME [ type ] ASSIGN expr SEMI
    def constdef(self) -> Optional[ConstDef]:
        print(blue(f"constdef(): next = {self.peek()}"))

        if not self.accept("CONST"):
            return None

        self.lookahead = None
        name = Name(self.expect("NAME").token)

        type_: Optional[str]
        if tok := self.accept("TYPE"):
            type_ = tok.token
            self.lookahead = None
        else:
            type_ = None

        self.expect("ASSIGN")
        value = self._literal()
        self.expect("SEMICOLON")

        node = ConstDef(name, type_, value)

        print(green(f"    parsed ConstDef {node}"))
        return node

    # expr : expr PLUS expr        (+)
    #      | expr MINUS expr       (-)
    #      | expr TIMES expr       (*)
    #      | expr DIVIDE expr      (/)
    #      | expr LT expr          (<)
    #      | expr LE expr          (<=)
    #      | expr GT expr          (>)
    #      | expr GE expr          (>=)
    #      | expr EQ expr          (==)
    #      | expr NE expr          (!=)
    #      | expr LAND expr        (&&)
    #      | expr LOR expr         (||)
    #      | PLUS expr
    #      | MINUS expr
    #      | LNOT expr              (!)
    #      | LPAREN expr RPAREN
    #      | location
    #      | literal
    #      | LBRACE statements RBRACE
    def expression(self) -> Optional[Expression]:
        print(blue(f"expression(): next = {self.peek()}"))

        if not (left := self._additive_term()):
            return None

        while tok := self.accept(
            "ADD", "SUB", "MUL", "DIV", "LT", "LE", "GT", "GE", "EQ", "NE", "LAND", "LOR"
        ):
            self.lookahead = None
            right = self._additive_term()
            assert right, "Expected right"
            left = BinOp(tok.token, left, right)  # type: ignore

        print(green(f"    parsed Expression {left}"))
        return left

    def _additive_term(self) -> Optional[Expression]:
        return self._literal() or self.name() or self._unary_op() or self.block()

    def _unary_op(self) -> Optional[UnaryOp]:
        if tok := self.accept("ADD", "SUB"):
            self.lookahead = None
            assert (expr := self.expression())
            return UnaryOp(tok.token, expr)

    def name(self) -> Optional[Name]:
        if tok := self.accept("NAME"):
            self.lookahead = None
            return Name(tok.token)

    # literal : INTEGER
    #         | FLOAT
    #         | CHAR
    #         | TRUE
    #         | FALSE
    #         | LPAREN RPAREN
    def _literal(self) -> Literal:
        return self.bool() or self.char() or self.integer() or self.float()

    def integer(self):
        if tok := self.accept("INTEGER"):
            self.lookahead = None
            return Integer(int(tok.token))

    def float(self):
        if tok := self.accept("FLOAT"):
            self.lookahead = None
            return Float(float(tok.token))

    def bool(self):
        if tok := self.accept("BOOL"):
            self.lookahead = None
            return Bool({"true": True, "false": False}[tok.token])

    def char(self):
        if tok := self.accept("CHAR"):
            self.lookahead = None
            return Char(tok.token)


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
