# parse.py
# flake8: noqa
#
# Wabbit parser.  The parser needs to construct the data model or an
# abstract syntax tree from text input.  The grammar shown here represents
# WabbitScript--a subset of the full Wabbit language.  It's written as
# a EBNF.  You will need to expand the grammar to include later features.
#
# Reference: https://github.com/dabeaz/compilers_2020_05/wiki/WabbitScript
#
# The following conventions are used:
#
#       ALLCAPS       --> A token
#       { symbols }   --> Zero or more repetitions of symbols
#       [ symbols ]   --> Zero or one occurences of symbols (optional)
#       s | t         --> Either s or t (a choice)
#
#
# statements : { statement }
#
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
# print_statement : PRINT expr SEMI
#
# assignment_statement : location ASSIGN expr SEMI
#
# variable_definition : VAR NAME [ type ] ASSIGN expr SEMI
#                     | VAR NAME type [ ASSIGN expr ] SEMI
#
# const_definition : CONST NAME [ type ] ASSIGN expr SEMI
#
# if_statement : IF expr LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]
#
# while_statement : WHILE expr LBRACE statements RBRACE
#
# break_statement : BREAK SEMI
#
# continue_statement : CONTINUE SEMI
#
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
#
# literal : INTEGER
#         | FLOAT
#         | CHAR
#         | TRUE
#         | FALSE
#         | LPAREN RPAREN
#
# location : NAME
#
# type      : NAME
#
# empty     :
# ======================================================================

# How to proceed:
#
# At first glance, writing a parser might look daunting. The key is to
# take it in tiny pieces.  Focus on one specific part of the language.
# For example, the print statement.  Start with something really basic
# like printing literals:
#
#     print 1;
#     print 2.5;
#
# From there, expand it to handle expressions:
#
#     print 2 + 3 * -4;
#
# Then, expand it to include variable names
#
#     var x = 3;
#     print 2 + x;
#
# Keep on expanding to more and more features of the language.  A good
# trajectory is to follow the programs found in the top level
# script_models.py file.  That is, write a parser that can recognize the
# source code for each part and build the corresponding model.  You
# will find yourself filling in pieces here throughout the project.
# It's ok to work piecemeal.
#
# Usage of tools:
#
# If you are highly motivated and want to know how a parser works at a
# low-level, you can write a hand-written recursive descent parser.
# It is also fine to use high-level tools such as
#
#    - SLY (https://github.com/dabeaz/sly),
#    - PLY (https://github.com/dabeaz/ply),
#    - ANTLR (https://www.antlr.org).

from .model import *
from .tokenize import WabbitLexer, tokenize
from sly import Parser


class WabbitParser(Parser):
    debugfile = 'parser.out'
    tokens = WabbitLexer.tokens      # Token names

    # program : statements
    @_('statements')
    def program(self, p):
        return p.statements
    #
    # statements : { statement }      # zero or more statements { }
    #
    @_('{ statement }')
    def statements(self, p):
        # p.statement   --- it's already a list of statement (by SLY)
        return Statements(*p.statement)

    @_('print_statement',
       'assignment_statement',
       'const_definition',
       'var_definition',
       'if_statement',
       'while_statement'
       )
    def statement(self, p):
        return p[0] # Just return whatever the thing is

    @_('expression SEMI')
    def statement(self, p):
        return ExpressionStatement(p.expression)


    @_('PRINT expression SEMI')
    def print_statement(self, p):
        return Print(p.expression)

    @_('location ASSIGN expression SEMI')
    def assignment_statement(self, p):
        return Assignment(p.location, LoadLocation(p.expression))

    @_('CONST NAME [ type ] ASSIGN expression SEMI')
    def const_definition(self, p):
        return Const(p.NAME.name, p.type, p.expression)

    @_('VAR NAME ASSIGN expression SEMI')
    def var_definition(self, p):
        return Var(p.NAME.name, Type(None), p.expression)

    @_('VAR NAME type [ ASSIGN expression ] SEMI')
    def var_definition(self, p):
        if p.ASSIGN:
            return Var(p.NAME.name, p.type, p.expression)
        else:
            return Var(p.NAME.name, p.type)

    @_('IF expression LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]')
    def if_statement(self, p):
        if p.ELSE:
            return If(p.expression, p.statements0, p.statements1)
        else:
            return If(p.expression, p.statements0)


    @_('WHILE expression LBRACE statements RBRACE')
    def while_statement(self, p):
        return While(self.expression, self.statements)

    @_('orterm [ LOR orterm ]')
    def expression(self, p):
        if p.LOR:
            return BinOp('||', p.orterm0, p.orterm1)
        else:
            return p.orterm0

# orterm:
    @_('andterm [ LAND andterm ]')
    def orterm(self, p):
        if p.LAND:
            return BinOp('&&', p.andterm0, p.andterm1)
        else:
            return p.andterm0


# andterm:
    @_('sumterm LT sumterm',
       'sumterm LE sumterm',
       'sumterm GT sumterm',
       'sumterm GE sumterm',
       'sumterm EQ sumterm',
       'sumterm NE sumterm')
    def andterm(self, p):
        if p.LT:
            return BinOp('<', p.sumterm0, p.sumterm1)
        elif p.LE:
            return BinOp('<=', p.sumterm0, p.sumterm1)
        if p.GT:
            return BinOp('>', p.sumterm0, p.sumterm1)
        elif p.GE:
            return BinOp('>=', p.sumterm0, p.sumterm1)
        if p.EQ:
            return BinOp('==', p.sumterm0, p.sumterm1)
        elif p.NE:
            return BinOp('!=', p.sumterm0, p.sumterm1)
        else:
            raise SyntaxError()

    @_('sumterm')
    def andterm(self, p):
        return p.sumterm

# sumterm:
    @_('multerm PLUS multerm',
       'multerm MINUS multerm')
    def sumterm(self, p):
        return BinOp(p[1], p.multerm0, p.multerm1)

    @_('multerm')
    def sumterm(self, p):
        return p.multerm

# multerm:
    @_('factor DIVIDE factor',
       'factor TIMES factor')
    def multerm(self, p):
        return BinOp(p[1], p.factor0, p.factor1)

    @_('factor')
    def multerm(self, p):
        return p.factor

# factor :
    @_('literal')
    def factor(self, p):
        return p.literal

    @_('location')
    def factor(self, p):
        return p.location

# factor :
    @_('PLUS expression',
       'MINUS expression',
       'LNOT expression')
    def factor(self, p):
        return UnaryOp(p[0], p.expression)


    @_('LBRACE statements RBRACE')
    def factor(self, p):
        return p.statements


# literal :

    @_('INTEGER')
    def literal(self, p):
        return Integer(int(p.INTEGER))


    @_('FLOAT',
       'CHAR',
       'TRUE',
       'FALSE',
       'LPAREN RPAREN'
       )
    def literal(self, p):
        if p.FLOAT:
            return Float(float(p.FLOAT))
        else:
            print("Other literals need to be implemented.")
            raise SyntaxError()

    @_('NAME')
    def location(self, p):
        return NamedLocation(repr(p.NAME))

    @_('NAME')
    def type(self, p):
        if p.NAME is not None:
            return Type(repr(p.NAME))
        else:
            return Type(None)

def parse_tokens(raw_tokens):
    parser = WabbitParser()
    return parser.parse(raw_tokens)

# Top-level function that runs everything
def parse_source(text):
    tokens = tokenize(text)
    model = parse_tokens(tokens)  # You need to implement this part
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
    model = parse(sys.argv[1])
    print(model)
