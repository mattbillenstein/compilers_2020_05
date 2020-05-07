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
from .tokenize import tokenize

# Magic token to signal end-of-file
class EOF:
    type = 'EOF'
    value = 'EOF'

class Tokens:
    def __init__(self, tokens):
        self.tokens = tokens        # <<< raw stream of tokens from the tokenizer (iterator/generator)
        self.lookahead = None       # Current token

    def peek(self):
        # Returns the current token, but without consuming it
        if self.lookahead is None:
            self.lookahead = next(self.tokens, EOF)    # Get the next token (or EOF)
        return self.lookahead

    def expect(self, toktype):
        # Requires the next token to have toktype or SyntaxError
        tok = self.peek()
        if tok.type != toktype:
            raise SyntaxError(f'Expected {toktype}. Got {tok.type})')
        self.lookahead = None       # Consume the token and return it
        return tok

    def accept(self, *toktypes):
        # Accept the next token if it has toktype, otherwise return None  (not an error)
        tok = self.peek()
        if tok.type not in toktypes:
            return None
        self.lookahead = None      # Consume the token
        return tok

        
# Grammar for Wabbit  (Specificiation of syntax)
#
# program : statements EOF      # End-of-file
def parse_program(tokens):
    statements = parse_statements(tokens)
    tokens.expect('EOF')
    return statements

# 
# statements : { statement }      # zero or more statements { }
#

def parse_statements(tokens):
    statements = [ ]
    while True:          # <<< How does this terminate cleanly????
        statement = parse_statement(tokens)
        if statement is None:
            break
        statements.append(statement)
    return Statements(statements)        # From the model

# statement : print_statement
#           | assignment_statement
#           | if_statement
#           | const_definition
#           | var_definition
#           | while_statement
#

def parse_statement(tokens):
    tok = tokens.peek()     # Look at the next token (does not consume)
    if tok.type == 'PRINT':
        return parse_print_statement(tokens)
    elif tok.type == 'CONST':
        return parse_const_definition(tokens)
    elif tok.type == 'VAR':
        return parse_var_definition(tokens)
    elif tok.type == 'IF':
        return parse_if_statement(tokens)
    elif tok.type == 'WHILE':
        return parse_while_statement(tokens)
    elif tok.type == 'NAME':                      
        return parse_expression_statement(tokens)         
    else:
        return None

# print_statement : PRINT expression SEMI
#
def parse_print_statement(tokens):
    tokens.expect('PRINT')      # Wishful thinking "expect" method
    try:
        expr = parse_expression(tokens)
    except SyntaxError as err:
        # Try to resynchronize the input on SEMI.
        while True:
            tok = tokens.peek()
            if tok.type != 'SEMI':
                # Eat the token and throw it away
                tokens.accept(tok.type)
            else:
                break
        tokens.expect('SEMI')
        raise SyntaxError("Bad print statement")
        
    tokens.expect('SEMI')
    return PrintStatement(expr)         #  Create a node from my model

# assignment_statement : location ASSIGN expression SEMI
#
def parse_assignment_statement(tokens):
    location = parse_location(tokens)
    tokens.expect('ASSIGN')     # ASSIGN -> '='
    expr = parse_expression(tokens)
    tokens.expect('SEMI')
    return AssignmentStatement(location, expr)   # Node from model

# const_definition : CONST NAME [ NAME ] ASSIGN expression SEMI
#
def parse_const_definition(tokens):
    tokens.expect('CONST')
    nametok = tokens.expect('NAME')
    typetok = tokens.accept('NAME')    # Read a token if it matches, return None otherwise
    tokens.expect('ASSIGN')   
    expr = parse_expression(tokens)
    tokens.expect('SEMI')
    return ConstDefinition(nametok.value, typetok.value if typetok else None, expr)

def parse_var_definition(tokens):
    tokens.expect('VAR')
    nametok = tokens.expect('NAME')
    typetok = tokens.accept('NAME')     # Optional type token.
    if tokens.accept('ASSIGN'):
        expr = parse_expression(tokens)
    else:
        expr = None
    tokens.expect('SEMI')
    return VarDefinition(nametok.value, typetok.value if typetok else None, expr)

def parse_if_statement(tokens):
    tokens.expect('IF')
    testexpr = parse_expression(tokens)
    tokens.expect('LBRACE')
    consequence = parse_statements(tokens)
    tokens.expect('RBRACE')
    if tokens.accept('ELSE'):
        tokens.expect('LBRACE')
        alternative = parse_statements(tokens)
        tokens.expect('RBRACE')
    else:
        alternative = Statements([])
    return IfStatement(testexpr, consequence, alternative)

def parse_while_statement(tokens):
    tokens.expect('WHILE')
    testexpr = parse_expression(tokens)
    tokens.expect('LBRACE')
    body = parse_statements(tokens)
    tokens.expect('RBRACE')
    return WhileStatement(testexpr, body)

def parse_expression_statement(tokens):
    expr = parse_expression(tokens)
    tokens.expect('SEMI')
    if isinstance(expr, Expression):
        return ExpressionStatement(expr)
    else:
        return expr

# Horrible hack. Pull assignment "location = expression" in and parse as if it
# were an expression involving a binary operator.  Then, pull it apart and
# transform it into an AssignmentStatement. This mess is caused by the fact
# that expressions can be used as statements. 

def parse_expression(tokens):
    leftterm = parse_orterm(tokens)
    if tokens.accept('ASSIGN'):
        rightterm = parse_orterm(tokens)
        if isinstance(leftterm, LoadLocation):
            return AssignmentStatement(leftterm.location, rightterm)
        else:
            raise SyntaxError("syntax error in location of assignment")
    return leftterm

def parse_orterm(tokens):
    leftterm = parse_andterm(tokens)
    while True:
        tok = tokens.accept('LOR')
        if tok:
            op = tok.value
            leftterm = BinOp(op, leftterm, parse_andterm(tokens))
        else:
            break
    return leftterm

def parse_andterm(tokens):
    leftterm = parse_relterm(tokens)
    while True:
        tok = tokens.accept('LAND')
        if tok:
            op = tok.value
            leftterm = BinOp(op, leftterm, parse_relterm(tokens))
        else:
            break
    return leftterm

def parse_relterm(tokens):
    leftterm = parse_addterm(tokens)
    while True:
        tok = tokens.accept('LT','LE','GT','GE','EQ','NE')
        if tok:
            op = tok.value
            leftterm = BinOp(op, leftterm, parse_addterm(tokens))
        else:
            break
    return leftterm

def parse_addterm(tokens):
    leftterm = parse_multerm(tokens)
    while True:
        tok = tokens.accept('PLUS','MINUS')
        if tok:
            op = tok.value
            leftterm = BinOp(op, leftterm, parse_multerm(tokens))
        else:
            break
    return leftterm

# term : factor { TIME|DIVIDE factor }        
#
def parse_multerm(tokens):
    leftfactor = parse_factor(tokens)
    while True:
        tok = tokens.accept('TIMES', 'DIVIDE')
        if tok:
            leftfactor = BinOp(tok.value, leftfactor, parse_factor(tokens))
        else:
            break
    return leftfactor

# factor : INTEGER | FLOAT | CHAR | LPAREN expression RPAREN | +/- expression
def parse_factor(tokens):
    tok = tokens.accept('INTEGER')
    if tok:
        return Integer(int(tok.value))
    tok = tokens.accept('FLOAT')
    if tok:
        return Float(float(tok.value))
    tok = tokens.accept('TRUE', 'FALSE')
    if tok:
        return Bool(tok.value == 'true')
    if tokens.accept('LPAREN'):
        expr = parse_expression(tokens)
        tokens.expect('RPAREN')
        return Grouping(expr)
    # Unary operator.... 
    tok = tokens.accept('PLUS','MINUS','LNOT')
    if tok:
        expr = parse_factor(tokens)     #<<<<< -2 + 3  << (-2) + 3
        return UnaryOp(tok.value, expr)
        
    tok = tokens.accept('LBRACE')
    if tok:
        statements = parse_statements(tokens)
        tokens.expect('RBRACE')
        return Compound(statements)
    # Only other option at this point is a location
    loc = parse_location(tokens)
    return LoadLocation(loc)

# location : NAME
def parse_location(tokens):
    tok = tokens.expect('NAME')
    return NamedLocation(tok.value)

def parse_tokens(raw_tokens):  
    tokens = Tokens(raw_tokens)
    return parse_program(tokens)

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


