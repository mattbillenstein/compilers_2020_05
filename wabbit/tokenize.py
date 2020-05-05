# wabbit/tokenize.py
#
# The role of a tokenizer is to turn raw text into recognized symbols
# known as tokens.
#
# The following set of tokens are defined for "WabbitScript".  Later
# parts of the project require you to add more tokens.  The suggested
# name of the token is on the left. The matching text is on the right.
#
# Reserved Keywords:
#     CONST   : 'const'
#     VAR     : 'var'
#     PRINT   : 'print'
#     BREAK   : 'break'
#     CONTINUE: 'continue'
#     IF      : 'if'
#     ELSE    : 'else'
#     WHILE   : 'while'
#     TRUE    : 'true'
#     FALSE   : 'false'
#
# Identifiers/Names
#     NAME    : Text starting with a letter or '_', followed by any number
#               number of letters, digits, or underscores.
#               Examples:  'abc' 'ABC' 'abc123' '_abc' 'a_b_c'
#
# Literals:
#     INTEGER :  123   (decimal)
#
#     FLOAT   : 1.234
#               .1234
#               1234.
#
#     CHAR    : 'a'     (a single character - byte)
#               '\xhh'  (byte value)
#               '\n'    (newline)
#               '\''    (literal single quote)
#
# Operators:
#     PLUS     : '+'
#     MINUS    : '-'
#     TIMES    : '*'
#     DIVIDE   : '/'
#     LT       : '<'
#     LE       : '<='
#     GT       : '>'
#     GE       : '>='
#     EQ       : '=='
#     NE       : '!='
#     LAND     : '&&'
#     LOR      : '||'
#     LNOT     : '!'
#
# Miscellaneous Symbols
#     ASSIGN   : '='
#     SEMI     : ';'
#     LPAREN   : '('
#     RPAREN   : ')'
#     LBRACE   : '{'
#     RBRACE   : '}'
#
# Comments:  To be ignored
#      //             Skips the rest of the line
#      /* ... */      Skips a block (no nesting allowed)
#
# Errors: Your lexer may optionally recognize and report the following
# error messages:
#
#      lineno: Illegal char 'c'
#      lineno: Unterminated character constant
#      lineno: Unterminated comment
#
# ----------------------------------------------------------------------


# High level function that takes input source text and turns it into tokens.
# This is a natural place to use some kind of generator function.

class Token:
    def __init__(self, type, value):
        self.type = type          # 'NUMBER'
        self.value = value        # '12345'

    def __repr__(self):
        return f'Token({self.type}, {self.value})'

import re

# def tokenize(text):
#     n = 0
#     while n < len(text):
#         if text[n] in {' ', '\t', '\n'}:    # Whitespace
#             n += 1;
#             continue                        # Skip
#
#         # Check for a comment.  /* .... bunch of random stuff ... */
#         if text[n:n+2] == '/*':
#             end = text.find("*/", n+2)
#             n = end + 2;
#             continue
#
#         # Question:
#         #    <=      --> TOKEN('LE')  or TOKEN('LT') TOKEN('EQ')
#         #    <       --> TOKEN('LT')   ??
#         if text[n] in {'+', '-', '*', '/'}:
#             yield Token('OP', text[n])
#             n += 1
#             continue
#
#         # Check for numbers
#         g = re.match(r'\d+', text[n:])
#         if g:
#             yield Token('NUMBER', g.group())
#             n += len(g.group())
#             continue

# Sample:
#
# for tok in tokenize("print 2 + 3 * 4;"):
#     print(tok)
#

# Tokenizing is based solved.  Not interesting.
# Tools available.

from sly import Lexer      # Disclaimer: I created SLY

class WabbitLexer(Lexer):
    reflags = re.MULTILINE

    # Valid token names
    tokens = {
        PLUS, MINUS, TIMES, DIVIDE, NUMBER, LT, LE, EQ, DECIMAL,
        GT, GE, EQ, NE, ASSIGN, LPAREN, RPAREN, LBRACE, RBRACE, SEMI,
        FLOAT, INTEGER, NAME, CHAR, PRINT, IF, CONST, VAR, ELSE, WHILE, BREAK, CONTINUE, COMMA,
        #LOOKUP,
        DCOLON,
        DOT
        }
    ignore = ' \t\n'       # Ignore these (between tokens)
    ignore_comment = r'//.*'
    ignore_block_comment = r'/\*((.|\n))*?\*/'
    _escape_sequences = [
        r'\\\\',
        r"\\'",
        r'\\\"',
        r'\\a',
        r'\\b',
        r'\\f',
        r'\\n',
        r'\\r',
        r'\\t',
        r'\\v',
        r'\\ooo',
        r'\\xhh',
    ]

    # Specify tokens as regex rules
    COMMA = r','
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    DCOLON = r':'
    FLOAT = r'(\d+\.\d*)|(\d*\.\d+)'      # 23.45
    INTEGER = r'\d+'
    CHAR = r'\'([\s\S]|' + '|'.join(_escape_sequences) + r')\''
    DOT = "\."
    #LOOKUP = r'\.[a-zA-Z_]([a-zA-Z_\d])*'
    NAME = r'[a-zA-Z_]([a-zA-Z_\d])*'
    print(CHAR)
    NAME['print'] = PRINT
    NAME['if'] = IF
    NAME['const'] = CONST
    NAME['var'] = VAR
    NAME['else'] = ELSE
    NAME['while'] = WHILE
    NAME['break'] = BREAK
    NAME['continue'] = CONTINUE



    # Put longer patterns first
    LE = r'<='
    LT = r'<'               # Order matters a lot. Definition order is the order matches are tried.
    GE = r'>='
    GT = r'>'
    EQ = r'=='
    NE = r'!='
    ASSIGN = r'='
    SEMI = r';'
    LPAREN =r'\('
    RPAREN = r'\)'
    LBRACE = r'{'
    RBRACE = r'}'

def tokenize(text):
    lexer = WabbitLexer()
    return lexer.tokenize(text)

# Main program to test on input files
def main(filename):
    with open(filename) as file:
        text = file.read()

    for tok in tokenize(text):
        print(tok)

if __name__ == '__main__':
    import sys
    main(sys.argv[1])
