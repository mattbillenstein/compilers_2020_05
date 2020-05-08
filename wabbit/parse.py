"""
program : statements EOF

statements : { statement }

statement : print_statement
          | assignment_statement
          | variable_definition
          | const_definition
          | func_definition
          | struct_definition
          | enum_definition
          | if_statement
          | if_let_statement
          | while_statement
          | while_let_statement
          | break_statement
          | continue_statement
          | return_statement
          | expression SEMI

print_statement : PRINT expression SEMI

assignment_statement : location ASSIGN expression SEMI

variable_definition : VAR NAME [ type ] ASSIGN expression SEMI
                    | VAR NAME type [ ASSIGN expression ] SEMI

const_definition : CONST NAME [ type ] ASSIGN expression SEMI

func_definition : FUNC NAME LPAREN [ parameters ] RPAREN type LBRACE statements RBRACE

parameters : parameter { COMMA parameter }
           | empty

parameter  : NAME type

struct_definition : STRUCT NAME LBRACE { struct_field } RBRACE

struct_field : NAME type SEMI

enum_definition : ENUM NAME LBRACE { enum_choice } RBRACE

enum_choice : NAME SEMI
            | NAME LPAREN type RPAREN

if_statement : IF expr LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]

if_let_statement : IF LET pattern ASSIGN expression LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]  # noqa

while_statement : WHILE expr LBRACE statements RBRACE

while_let_statement : WHILE LET pattern ASSIGN expression LBRACE statements RBRACE

break_statement : BREAK SEMI

continue_statement : CONTINUE SEMI

return_statement : RETURN expression SEMI

expression : orterm { LOR ortem }

orterm : andterm { LAND andterm }

andterm : sumterm { LT|LE|GT|GE|EQ|NE sumterm }

sumterm : multerm { PLUS|MINUS multerm }

multerm : factor { TIMES|DIVIDE factor }

factor : literal
       | location
       | enum_value
       | match
       | LPAREN expression RPAREN
       | PLUS expression
       | MINUS expression
       | LNOT expression
       | NAME LPAREN exprlist RPAREN
       | LBRACE statements RBRACE

literal : INTEGER
        | FLOAT
        | CHAR
        | TRUE
        | FALSE
        | LPAREN RPAREN

exprlist : expression { COMMA expression }
         | empty

location : NAME
         | expression DOT NAME

enum_value : NAME DCOLON NAME
           | NAME DCOLON NAME LPAREN expression RPAREN

match : MATCH expression LBRACE { matchcase } RBRACE

matchcase : pattern ARROW expression SEMI

pattern   : NAME
          | NAME LPAREN NAME RPAREN

type      : NAME
"""
from dataclasses import dataclass
from typing import ClassVar
from typing import Optional

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
    Node,
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

_print = print

DEBUG = False


def print(*args, **kwargs):
    if DEBUG:
        _print(*args, **kwargs)


@dataclass
class BaseParser:
    tokens: TokenStream
    lookahead: Optional[Token] = None
    line_num: int = 0
    line_num_map: ClassVar = {}

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
        self.line_num = tok.line_num
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
            self.line_num = tok.line_num
            return tok
        # print(blue("    -> reject"))


class Parser(BaseParser):
    def program(self) -> Statements:
        statements = self.statements()
        self.expect("EOF")  # TODO
        node = statements

        print(green(f"parsed Program: {node}"))
        return node

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

    def statement(self) -> Optional[Statement]:
        print(blue(f"statement(): next = {self.peek()}"))

        statement = (
            self.print_()
            or self.vardef()
            or self.constdef()
            or self.if_()
            or self.while_()
            or self.assign()
            or self.expression()
        )

        if statement:
            print(green(f"    parsed Statement: {statement}"))
            self.accept("SEMICOLON")
            return statement

    def if_(self) -> Optional[Statement]:
        print(blue(f"if(): next = {self.peek()}"))

        if not self.accept("IF"):
            return None

        assert (test := self.expression())
        assert (then := self.block())
        else_ = self._else()
        node = If(test, then.statements, else_.statements if else_ else None)
        print(green(f"    parsed If: {node}"))
        return node

    def _else(self) -> Optional[Block]:
        if not self.accept("ELSE"):
            return None
        assert (block := self.block())
        return block

    def while_(self) -> Optional[Statement]:
        print(blue(f"while(): next = {self.peek()}"))

        if not self.accept("WHILE"):
            return None

        assert (test := self.expression())
        assert (then := self.block())
        node = While(test, then.statements)
        print(green(f"    parsed While: {node}"))
        return node

    def block(self) -> Optional[Block]:
        if not self.accept("LBRACE"):
            return None
        statements = self.statements()
        self.expect("RBRACE")
        return Block(statements)

    def print_(self) -> Optional[Statement]:
        print(blue(f"print(): next = {self.peek()}"))

        if not self.accept("PRINT"):
            return None

        assert (expression := self.expression())
        self.expect("SEMICOLON")
        node = Print(expression)

        print(green(f"    parsed Print: {node}"))
        return node

    def assign(self) -> Optional[Statement]:
        print(blue(f"assign(): next = {self.peek()}"))

        if not (tok := self.accept("NAME")):  # TODO: location
            return None
        location = Location(tok.token)

        self.expect("ASSIGN")

        assert (expression := self.expression())
        self.expect("SEMICOLON")
        node = Assign(location, expression)

        print(green(f"    Parsed Assign: {node}"))
        return node

    def vardef(self) -> Optional[VarDef]:
        print(blue(f"vardef(): next = {self.peek()}"))

        if not self.accept("VAR"):
            return None

        name = Name(self.expect("NAME").token)

        type_: Optional[str]
        if tok := self.accept("TYPE"):
            type_ = tok.token
        else:
            type_ = None

        if self.accept("ASSIGN"):
            assert (value := self.expression())
        else:
            value = None
            assert type_

        self.expect("SEMICOLON")
        node = VarDef(name, type_, value)

        print(green(f"    parsed VarDef {node}"))
        return node

    def constdef(self) -> Optional[ConstDef]:
        print(blue(f"constdef(): next = {self.peek()}"))

        if not self.accept("CONST"):
            return None

        name = Name(self.expect("NAME").token)

        type_: Optional[str]
        if tok := self.accept("TYPE"):
            type_ = tok.token
        else:
            type_ = None

        self.expect("ASSIGN")
        value = self._literal()
        self.expect("SEMICOLON")

        node = ConstDef(name, type_, value)

        print(green(f"    parsed ConstDef {node}"))
        return node

    def expression(self) -> Optional[Expression]:
        parse_multerm = self._make_expression_parser(["MUL", "DIV"], self._factor)
        parse_addterm = self._make_expression_parser(["ADD", "SUB"], parse_multerm)
        parse_relterm = self._make_expression_parser(
            ["LT", "LE", "GT", "GE", "EQ", "NE"], parse_addterm
        )
        parse_andterm = self._make_expression_parser(["LAND"], parse_relterm)
        parse_orterm = self._make_expression_parser(["LOR"], parse_andterm)

        return parse_orterm(self)

    def _make_expression_parser(self, operators, child_parser):
        def parser(self) -> Optional[Expression]:
            print(blue(f"expression({operators}): next = {self.peek()}"))
            left = child_parser(self)
            while tok := self.accept(*operators):
                assert (right := child_parser(self))
                left = BinOp(tok.token, left, right)
            print(green(f"    parsed {left}"))
            return left

        return parser

    @staticmethod
    def _factor(self):
        # TODO: LPAREN
        return self._literal() or self.name() or self._unary_op() or self.block()

    def _unary_op(self) -> Optional[UnaryOp]:
        if tok := self.accept("ADD", "SUB", "LNOT"):
            assert (expr := self._factor(self))
            return UnaryOp(tok.token, expr)

    def name(self) -> Optional[Name]:
        if tok := self.accept("NAME"):
            return Name(tok.token)

    def _literal(self) -> Literal:
        return self.bool() or self.char() or self.integer() or self.float()

    def integer(self):
        if tok := self.accept("INTEGER"):
            return Integer(int(tok.token))

    def float(self):
        if tok := self.accept("FLOAT"):
            return Float(float(tok.token))

    def bool(self):
        if tok := self.accept("BOOL"):
            return Bool({"true": True, "false": False}[tok.token])

    def char(self):
        if tok := self.accept("CHAR"):
            return Char(tok.token)


def parse_source_debug(source):
    from wabbit.interp import interpret_program
    from utils import print_source, print_diff
    from .format_source import format_source

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

    # Interpret
    print(interpret_program(model))

    return model


def parse_source(source, debug=False):
    global DEBUG
    DEBUG |= debug

    if DEBUG:
        return parse_source_debug(source)
    else:
        return Parser(tokenize(source)).statements()


def parse_file(path, debug=False):
    global DEBUG
    DEBUG |= debug

    with open(path) as file:
        source = file.read()

    return parse_source(source)


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    if args[0] == "-d":
        DEBUG = True
        args = args[1:]

    parse_file(args[0])
