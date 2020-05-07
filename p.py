# p.py
#
# Example: of hand-written parser.  (Recursive Descent parsing).
from wabbit.model import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens         # The stream of tokens
        self.lookahead = None        # The current token on the input

    def peek(self):
        # Return the current token without consuming it
        if not self.lookahead:
            self.lookahead = next(self.tokens)
        return self.lookahead

    def expect(self, toktype):
        # Look for a token and consume it
        tok = self.peek()     # Get the next token
        if tok.type == toktype:
            self.lookahead = None
        else:
            raise SyntaxError()
        return tok

def parse_print_statement(parser):
    # tokens is generator/iterator producing tokens
    #
    # Parse a statement of the form
    #
    #     PRINT expression ;
    #
    parser.expect('PRINT')
    expression = parse_expression(parser)
    parser.expect('SEMI')
    return PrintStatement(expression)    # Needs expression. From somewhere

def parse_expression(parser):
    # What is the syntax of an expression????
    #
    # Consider:    2 + 3 * 4
    #
    #   expression : term  { +|- term }
    #                      ^^^^^^^^^^^^^^
    #                      zero or more repetition of additional terms
    #
    #  term        : factor { *|/ factor }
    #
    #  factor      : INTEGER                          # simple parts
    #              | FLOAT
    #              | LPAREN expression RPAREN
    #

    leftterm = parse_term(parser)      # Has to have at least one term
    # Peek ahead to see if there is an optional part coming
    while True:
        tok = parser.peek()
        if tok.type in { "PLUS", "MINUS" }:
            op = parser.expect(tok.type)     # Consume the operator token
            rightterm = parse_term(parser)
            leftterm = BinOp(op.value, leftterm, rightterm)
        else:
            break

    return leftterm

def parse_term(parser):
    leftfactor = parse_factor(parser)      # Has to have at least one factor
    # Peek ahead to see if there is an optional part coming
    while True:
        tok = parser.peek()
        if tok.type in { "TIMES", "DIVIDE" }:
            op = parser.expect(tok.type)     # Consume the operator token
            rightfactor = parse_factor(parser)
            leftfactor = BinOp(op.value, leftfactor, rightfactor)
        else:
            break

    return leftfactor

def parse_factor(parser):
    tok = parser.peek()        # Look at the next token (DO NOT CONSUME)
    if tok.type == 'INTEGER':
        tok = parser.expect('INTEGER')    # Consume the token
        return Integer(int(tok.value))    # Returns too early....  2 + 3 + 4;
    elif tok.type == 'FLOAT':
        tok = parser.expect('FLOAT')
        return Float(float(tok.value))
    elif tok.type == 'LPAREN':
        parser.expect('LPAREN')
        expr = parse_expression(parser)    # Call myself for inner expression
        parser.expect('RPAREN')
        return Grouping(expr)
    else:
        raise SyntaxError()

from wabbit.tokenize import tokenize
