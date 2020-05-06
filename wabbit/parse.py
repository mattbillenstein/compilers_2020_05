# parse.py
#
# Wabbit parser.  The parser needs to construct the data model or an
# abstract syntax tree from text input.  The grammar shown here represents
# WabbitScript--a subset of the full Wabbit language.  It's written as
# a EBNF.  You will need to expand the grammar to include later features.
#
# Reference: https://github.com/dabeaz/compilers_2020_05/wiki/WabbitScript
#
# program : statements EOF

# statements : { statement }

# statement : print_statement
#           | assignment_statement
#           | variable_definition
#           | const_definition
#           | func_definition
#           | struct_definition
#           | enum_definition
#           | if_statement
#           | if_let_statement
#           | while_statement
#           | while_let_statement
#           | break_statement
#           | continue_statement
#           | return_statement
#           | expression SEMI

# print_statement : PRINT expression SEMI

# assignment_statement : location ASSIGN expression SEMI

# variable_definition : VAR NAME [ type ] ASSIGN expression SEMI
#                     | VAR NAME type [ ASSIGN expression ] SEMI

# const_definition : CONST NAME [ type ] ASSIGN expression SEMI

# func_definition : FUNC NAME LPAREN [ parameters ] RPAREN type LBRACE statements RBRACE

# parameters : parameter { COMMA parameter }
#            | empty

# parameter  : NAME type

# struct_definition : STRUCT NAME LBRACE { struct_field } RBRACE

# struct_field : NAME type SEMI

# enum_definition : ENUM NAME LBRACE { enum_choice } RBRACE

# enum_choice : NAME SEMI
#             | NAME LPAREN type RPAREN

# if_statement : IF expr LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]

# if_let_statement : IF LET pattern ASSIGN expression LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]

# while_statement : WHILE expr LBRACE statements RBRACE

# while_let_statement : WHILE LET pattern ASSIGN expression LBRACE statements RBRACE

# break_statement : BREAK SEMI

# continue_statement : CONTINUE SEMI

# return_statement : RETURN expression SEMI

# expression : orterm { LOR ortem }

# orterm : andterm { LAND andterm }

# andterm : sumterm { LT|LE|GT|GE|EQ|NE sumterm }

# sumterm : multerm { PLUS|MINUS multerm }

# multerm : factor { TIMES|DIVIDE factor }

# factor : literal
#        | location
#        | enum_value
#        | match
#        | LPAREN expression RPAREN
#        | PLUS expression
#        | MINUS expression
#        | LNOT expression
#        | NAME LPAREN exprlist RPAREN
#        | LBRACE statements RBRACE

# literal : INTEGER
#         | FLOAT
#         | CHAR
#         | TRUE
#         | FALSE
#         | LPAREN RPAREN

# exprlist : expression { COMMA expression }
#          | empty

# location : NAME
#          | expression DOT NAME

# enum_value : NAME DCOLON NAME
#            | NAME DCOLON NAME LPAREN expression RPAREN

# match : MATCH expression LBRACE { matchcase } RBRACE

# matchcase : pattern ARROW expression SEMI

# pattern   : NAME
#           | NAME LPAREN NAME RPAREN

# type      : NAME

# empty     :
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

from sly import Parser
from .model import *
from .tokenize import tokenize, WabbitLexer


class WabbitParser(Parser):
    tokens = WabbitLexer.tokens

    @_("orterm LOR orterm")
    def expression(self, p):
        return BinOp("||", p.orterm0, p.orterm1)

    @_("orterm")
    def expression(self, p):
        return p.orterm

    @_("andterm LAND andterm")
    def orterm(self, p):
        return BinOp("&&", p.andterm0, p.andterm1)

    @_("andterm")
    def expression(self, p):
        return p.andterm

    @_("sumterm LT sumterm")
    def andterm(self, p):
        return BinOp("<", p.sumterm0, p.sumterm1)

    @_("sumterm LE sumterm")
    def andterm(self, p):
        return BinOp("<=", p.sumterm0, p.sumterm1)

    @_("sumterm GT sumterm")
    def andterm(self, p):
        return BinOp(">", p.sumterm0, p.sumterm1)

    @_("sumterm GE sumterm")
    def andterm(self, p):
        return BinOp(">=", p.sumterm0, p.sumterm1)

    @_("sumterm EQ sumterm")
    def andterm(self, p):
        return BinOp("==", p.sumterm0, p.sumterm1)

    @_("sumterm NE sumterm")
    def andterm(self, p):
        return BinOp("!=", p.sumterm0, p.sumterm1)

    @_("sumterm")
    def expression(self, p):
        return p.sumterm

    @_("multerm PLUS multerm")
    def sumterm(self, p):
        return BinOp("+", p.multerm0, p.multerm1)

    @_("multerm MINUS multerm")
    def sumterm(self, p):
        return BinOp("-", p.multerm0, p.multerm1)

    @_("factor TIMES factor")
    def multerm(self, p):
        return BinOp("*", p.factor0, p.factor1)

    @_("factor DIVIDE factor")
    def multerm(self, p):
        return BinOp("/", p.factor0, p.factor1)

    @_("literal")
    def factor(self, p):
        return p.literal

    @_("INTEGER")
    def literal(self, p):
        return Integer(int(p.INTEGER))

    @_("FLOAT")
    def literal(self, p):
        return Float(float(p.FLOAT))

    @_("NAME LPAREN NAME RPAREN")
    def pattern(self, p):
        return Arguments(Argument(p.name0), Argument(p.name1))

    @_("NAME")
    def pattern(self, p):
        return p.NAME

    @_("NAME")
    def type(self, p):
        return p.NAME

    @_("")
    def empty(self, p):
        pass


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

