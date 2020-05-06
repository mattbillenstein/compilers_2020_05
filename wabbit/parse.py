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

from .model import *
from .tokenize import tokenize, WabbitLexer
from sly import Parser

class WabbitParser(Parser):
    tokens = WabbitLexer.tokens
    precedence = (
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE),
        )

    @_('{ statement }')
    def statements(self, p):
        return Statements(p.statement)

    # STATEMENTS===============================
    @_('expr SEMI')
    def statement(self, p):
        return p[0]

    @_('PRINT expr SEMI')
    def statement(self, p):
        return PrintStatement(p[1])

    @_('VAR NAME [ NAME ] [ ASSIGN expr ] SEMI')
    def statement(self, p):
        result = Var(p.NAME0, p.NAME1)
        if p.ASSIGN is not None:
            result = Assign(result, p.expr)
        return result

    @_('CONST NAME ASSIGN expr SEMI')
    def statement(self, p):
        result = Const(p.NAME, p.expr)
        return result

    @_('NAME ASSIGN expr SEMI')
    def statement(self, p):
        return Assign(Variable(p.NAME), p.expr)

    @_('IF expr LBRACE statements RBRACE ELSE LBRACE statements RBRACE')
    def statement(self, p):
        return IfElse(p.expr, p.statements0, p.statements1)

    @_('WHILE expr LBRACE statements RBRACE')
    def statement(self, p):
        return While(p.expr, p.statements)

    @_('FUNC NAME LPAREN [ arguments ] RPAREN [ NAME ] LBRACE statements RBRACE')
    def statement(self, p):
        return Function(p.NAME0, p.arguments, p.NAME1, p.statements)

    @_('RETURN expr SEMI')
    def statement(self, p):
        return Return(p.expr)

    @_('{ argument }')
    def arguments(self, p):
        return Arguments(p.argument)

    @_('NAME NAME [ COMMA ]')
    def argument(self, p):
        return Argument(p[0], p[1])

    # EXPRESSIONS==============================
    @_('NUMBER')
    def expr(self, p):
        return Integer(int(p[0]))

    @_('DECIMAL')
    def expr(self, p):
        return Float(float(p.DECIMAL))

    @_('expr PLUS expr',
        'expr MINUS expr',
        'expr TIMES expr',
        'expr DIVIDE expr',
        'expr LT expr',
            )
    def expr(self, p):
        return BinOp(p[1], p[0], p[2])

    @_('NAME')
    def expr(self, p):
        return Variable(p.NAME)

    @_('PLUS expr', 'MINUS expr', 'LNOT expr')
    def expr(self, p):
        return UnaryOp(p[0], p.expr)

    @_('LBRACE statements RBRACE')
    def expr(self, p):
        return CompoundExpression(p.statements)

    @_('NAME LPAREN { invoking_argument } RPAREN')
    def expr(self, p):
        return FunctionInvocation(p.NAME, InvokingArguments(p.invoking_argument))

    @_('expr [ COMMA ]')
    def invoking_argument(self, p):
        return InvokingArgument(p.expr)

def parse_tokens(tokens):
    parser = WabbitParser()
    return parser.parse(tokens)

# Top-level function that runs everything
def parse_source(text):
    tokens = tokenize(text)
    model = parse_tokens(tokens)     # You need to implement this part
    return model

# Example of a main program
def parse_file(filename):
    with open(filename) as file:
        text = file.read()
    return parse_source(text)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        raise SystemExit('Usage: wabbit.parse filename')
    model = parse(sys.argv[1])
    print(model)


