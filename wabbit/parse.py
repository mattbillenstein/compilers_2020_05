# parse.py
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

import os.path
import sys

import sly

from .model import *
from .tokenize import tokenize, WabbitLexer


class WabbitParser(sly.Parser):
#    debugfile = 'parser.txt'

    tokens = WabbitLexer.tokens

    precedence = [
        ('left', LOR),
        ('left', LAND),
        ('left', LT, LE, GT, GE, EQ, NE),
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE),
        ('right', UNARY),   # +, -, !
    ]

    @_('{ node }')
    def block(self, p):
        return Block(p.node)

    @_('node SEMI')
    def node(self, p):
        return p.node

    @_('LPAREN node RPAREN')
    def node(self, p):
        return p.node

    @_(*[f'{op} node %prec UNARY' for op in WabbitLexer._unaop])
    def node(self, p):
        return UnaOp(p[0], p.node)

    @_(*[f'node {op} node' for op in WabbitLexer._binop])
    def node(self, p):
        op = p[1]
        left = p.node0
        right = p.node1
        return BinOp(op, left, right)

    @_('PRINT node SEMI')
    def node(self, p):
        return Print(p.node)

    @_('VAR name [ type ] ASSIGN node SEMI')
    def node(self, p):
        return Var(p.name, p.node, p.type)

    @_('VAR name type SEMI')
    def node(self, p):
        return Var(p.name, type=p.type)

    @_('CONST name [ type ] ASSIGN node SEMI')
    def node(self, p):
        return Const(p.name, p.node, type=p.type)

    @_('IF node LBRACE block RBRACE [ ELSE LBRACE block RBRACE ]')
    def node(self, p):
        return If(p.node, p.block0, p.block1)

    @_('WHILE node LBRACE block RBRACE')
    def node(self, p):
        return While(p.node, p.block)

    @_('LBRACE block RBRACE')
    def node(self, p):
        return Compound(p.block.statements)

    @_('FUNC name LPAREN [ argdefs ] RPAREN [ type ] LBRACE block RBRACE')
    def node(self, p):
        return Func(p.name, p.block, p.argdefs, p.type)

    @_('argdef { COMMA argdef }')
    def argdefs(self, p):
        return [p.argdef0] + p.argdef1

    @_('name type')
    def argdef(self, p):
        return ArgDef(p.name, p.type)

    @_('name LPAREN [ callargs ] RPAREN')
    def node(self, p):
        return Call(p.name, p.callargs)

    @_('node { COMMA node }')
    def callargs(self, p):
        return [p.node0] + p.node1

    @_('RETURN node SEMI')
    def node(self, p):
        return Return(p.node)

    @_('name ASSIGN node SEMI')
    def node(self, p):
        return Assign(p.name, p.node)

    @_('name DOT NAME')
    def name(self, p):
        return Attribute(p.name, p.NAME)

    @_('STRUCT NAME LBRACE field SEMI { field SEMI } RBRACE')
    def node(self, p):
        return Struct(Name(p.NAME), [p.field0] + p.field1)

    @_('name type')
    def field(self, p):
        return Field(p.name, p.type)

    @_('INTEGER')
    def node(self, p):
        return Integer(int(p.INTEGER))

    @_('FLOAT')
    def node(self, p):
        return Float(float(p.FLOAT))

    @_('CHAR')
    def node(self, p):
        return Char(p.CHAR)

    @_('TRUE')
    def node(self, p):
        return Bool(True)

    @_('FALSE')
    def node(self, p):
        return Bool(False)

    @_('LPAREN RPAREN')
    def node(self, p):
        return UNIT

    @_('BREAK')
    def node(self, p):
        return Break()

    @_('CONTINUE')
    def node(self, p):
        return Continue()

    @_('name')
    def node(self, p):
        return p.name

    @_('NAME')
    def name(self, p):
        return Name(p.NAME)

    @_('NAME')
    def type(self, p):
        return Type(p.NAME)


def parse(text):
    tokens = tokenize(text)
    parser = WabbitParser()
    model = parser.parse(tokens)
    return model

def main(args):
    if args:
        if os.path.isfile(args[0]):
            with open(args[0]) as file:
                text = file.read()
        else:
            text = args[0]
    else:
        text = sys.stdin.read()

    print(parse(text))

if __name__ == '__main__':
    main(sys.argv[1:])
