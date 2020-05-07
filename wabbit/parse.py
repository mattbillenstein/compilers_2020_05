# wabbit/parse.py
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
#         | LPAREN RPAREN        # unit
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
        
# Grammar for Wabbit  (Specificiation of syntax)
#

class WabbitParser(Parser):
    # debugfile = 'parser.out'
    tokens = WabbitLexer.tokens      # Token names

    precedence = [
        ('left', LOR),       # a || b
        ('left', LAND),      # a && b
        ('left', LT, LE, GT, GE, EQ, NE),     #  2 + 3 < 4 + 5   -> (2 + 3) <  (4 + 5)
        ('left', PLUS, MINUS),       # Lower precedence      2 + 3 + 4 --> (2+3) + 4
        ('left', TIMES, DIVIDE),     # Higher precedence     2 + 3 * 4 --> 2 + (3 * 4)  (preference for the TIMES)

        # Unary -x.   -> Super high precedence    2 * -x.
        ('right', UNARY),    # 'UNARY' is a fake token (does not exist in tokenizer). Used below with %prec.
        ]
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
        return Statements(p.statement)

    # statement : print_statement
    #           | assignment_statement
    #           | if_statement
    #           | const_definition
    #           ...
    #
    @_('print_statement',
       'assignment_statement',
       'const_definition',
       'var_definition',
       'if_statement',
       'while_statement',
       'break_statement',
       'continue_statement',
       'expression_statement',
       )
    def statement(self, p):
        return p[0]               # Just return whatever the thing is

    # print_statement : PRINT expression SEMI
    #
    @_('PRINT expression SEMI')
    def print_statement(self, p):      # p contains all information from the parse
        # Create a node from your model
        node = PrintStatement(p.expression, lineno=p.lineno)   # p.lineno is line of left-most token
        return node

    # Error version
    @_('PRINT error SEMI')
    def print_statement(self, p):
        print("Bad print statement")
        return PrintStatement(Integer(0))   # Have to return something.(Compiler will stop anyways because of error)

    # assignment_statement : location ASSIGN expression SEMI
    #
    @_('location ASSIGN expression SEMI')
    def assignment_statement(self, p):
        return AssignmentStatement(p.location, p.expression, lineno=p.lineno)

    # const_definition : CONST NAME [ NAME ] ASSIGN expression SEMI
    #
    @_('CONST NAME [ type ] ASSIGN expression SEMI')
    def const_definition(self, p):
        return ConstDefinition(p.NAME, p.type, p.expression, lineno=p.lineno)

    @_('VAR NAME [ type ] [ ASSIGN expression ] SEMI')
    def var_definition(self, p):
        # Do we check for both missing type/expression here?  Is it a syntax error?
        # Is it some other kind of error?  Let's ignore the error for the moment.
        return VarDefinition(p.NAME, p.type, p.expression, lineno=p.lineno)

    @_('IF expression LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]')
    def if_statement(self, p):
        return IfStatement(p.expression, p.statements0, p.statements1 if p.statements1 else Statements([]),
                           lineno=p.lineno)

    @_('WHILE expression LBRACE statements RBRACE')
    def while_statement(self, p):
        return WhileStatement(p.expression, p.statements, lineno=p.lineno)
    
    @_('BREAK SEMI')
    def break_statement(self, p):
        return BreakStatement(lineno=p.lineno)

    @_('CONTINUE SEMI')
    def continue_statement(self, p):
        return ContinueStatement(lineno=p.lineno)

    @_('expression SEMI')
    def expression_statement(self, p):
        return ExpressionStatement(p.expression, lineno=p.expression.lineno)

    @_('expression PLUS expression',
       'expression MINUS expression',
       'expression TIMES expression',
       'expression DIVIDE expression',
       'expression LT expression',
       'expression LE expression',
       'expression GT expression',
       'expression GE expression',
       'expression EQ expression',
       'expression NE expression',
       'expression LAND expression',
       'expression LOR expression',
       )
    def expression(self, p):
        op = p[1]           
        left = p.expression0
        right = p.expression1
        return BinOp(op, left, right, lineno=p.lineno)

    @_('PLUS expression %prec UNARY',      # Use the high precedence of the fake "UNARY" token
       'MINUS expression %prec UNARY',     # based on "yacc"  (yet another compiler compiler)
       'LNOT expression %prec UNARY')      # Rewrite the grammar to not have ambiguity.
    def expression(self, p):
        return UnaryOp(p[0], p.expression, lineno=p.lineno)

    @_('LPAREN expression RPAREN')
    def expression(self, p):
        return Grouping(p.expression, lineno=p.lineno)

    @_('LBRACE statements RBRACE')
    def expression(self, p):
        return Compound(p.statements, lineno=p.lineno)

    @_('location')
    def expression(self, p):
        return LoadLocation(p.location, lineno=p.location.lineno)

    @_('INTEGER')           # triggers
    def expression(self, p):
        return Integer(int(p.INTEGER), lineno=p.lineno)
    
    @_('FLOAT')
    def expression(self, p):
        return Float(float(p.FLOAT), lineno=p.lineno)

    @_('CHAR')
    def expression(self, p):
        # Could be better..... alternative: write a real parser for escape codes.
        # Cheating: test programs only use normal characters and '\n'.
        return Char(eval(p.CHAR), lineno=p.lineno)     # "'\n'" --> eval() --> '\n'

    @_('TRUE')
    def expression(self, p):
        return Bool(True, lineno=p.lineno)

    @_('FALSE')
    def expression(self, p):
        return Bool(False, lineno=p.lineno)

    @_('NAME')
    def location(self, p):
        return NamedLocation(p.NAME, lineno=p.lineno)

    @_('NAME')
    def type(self, p):
        return p.NAME

def parse_tokens(raw_tokens):  
    parser = WabbitParser()
    return parser.parse(raw_tokens)

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
    model = parse_file(sys.argv[1])
    print(model)


