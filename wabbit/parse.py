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
        print(blue(f"accept({types_}) next = {self.peek()}"))
        tok = self.peek()
        if tok.type_ in types_:
            print(green(f"    -> {tok}"))
            self.lookahead = None
            return tok
        print(blue("    -> reject"))
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
            or self.assign()
            or self.vardef()
            or self.constdef()
            or self.if_()
            or self.expression()
        )

        if statement:
            print(green(f"    parsed Statement: {statement}"))
        return statement

    # if_statement : IF expr LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]
    def if_(self) -> Optional[Statement]:
        if self.accept("IF"):
            self.lookahead = None
        else:
            return None
        test = self.expression()
        then = self.block()
        else_ = self._else()
        return If(test, then.statements, else_.statements if else_ else None)

    def _else(self) -> Optional[Block]:
        if not self.accept("ELSE"):
            return None
        self.lookahead = None
        return self.block()

    def while_(self) -> Optional[Statement]:
        if self.accept("WHILE"):
            self.lookahead = None
        else:
            return None
        test = self.expression()
        then = self.block()
        return While(test, then.statements)

    def block(self) -> Block:
        # TODO: this demands a block, whereas most methods return Optional[Node]
        self.expect("LBRACE")
        statements = self.statements()  # TODO: how does termination work?!
        self.expect("RBRACE")
        return Block(statements)

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

        expression = self.expression()
        self.expect("SEMICOLON")
        node = Assign(location, expression)

        print(green(f"    Parsed Assign: {node}"))
        return node

    # variable_definition : VAR NAME [ type ] ASSIGN expr SEMI
    #                     | VAR NAME type [ ASSIGN expr ] SEMI
    def vardef(self) -> Optional[VarDef]:
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

        print(green(f"    parsed VarDef {node}"))
        return node

    # const_definition : CONST NAME [ type ] ASSIGN expr SEMI
    def constdef(self) -> Optional[ConstDef]:
        print(blue(f"constdef(): next = {self.peek()}"))

        if self.accept("CONST"):
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
    def expression(self) -> Expression:
        print(blue(f"expression(): next = {self.peek()}"))

        left = self._literal() or self.name()  # TODO: arbitrary expression
        if not left:
            raise RuntimeError(f"Error parsing expression: next = {self.peek()}")

        if tok := self.accept(
            "PLUS", "MINUS", "TIMES", "DIVIDE", "LT", "LE", "GT", "GE", "EQ", "NE", "LAND", "LOR"
        ):
            self.lookahead = None
            right = self._literal() or self.name()  # TODO: arbitrary expression
            assert right, "Expected right"
            left = BinOp(tok.token, left, right)  # type: ignore

        print(green(f"    parsed Expression {left}"))
        return left

    def name(self) -> Optional[Name]:
        if tok := self.accept("NAME"):
            self.lookahead = None
            return Name(tok.token)
        else:
            return None

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
        else:
            return None

    def float(self):
        if tok := self.accept("FLOAT"):
            self.lookahead = None
            return Float(float(tok.token))
        else:
            return None

    def bool(self):
        if tok := self.accept("BOOL"):
            self.lookahead = None
            return Bool({"true": True, "false": False}[tok.token])
        else:
            return None

    def char(self):
        if tok := self.accept("CHAR"):
            self.lookahead = None
            return Char(tok.token)
        else:
            return None


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
