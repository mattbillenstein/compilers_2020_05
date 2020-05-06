# tokenizer.py
# flake8: noqa
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

from sly import Lexer

class WabbitLexer(Lexer):

    ignore = ' \t\n'

    tokens = {CONST, VAR, PRINT, BREAK, CONTINUE, IF, ELSE, WHILE, TRUE, FALSE,
        NAME, FLOAT, INTEGER, CHAR, LE, GE, EQ, NE, LAND, LOR, PLUS, MINUS, TIMES,
        DIVIDE, LT, GT, LNOT, ASSIGN, SEMI, LPAREN, RPAREN, LBRACE, RBRACE, DOT}

    ignore_eol_comments = r'//.*'
    ignore_comments = r'/\*(.|\n)*?\*/'

    # The following is adopted from Spencer
    _escape_sequences = "|".join([
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
    ])

# Reserved Keywords:
    CONST   = r'const'
    VAR     = r'var'
    PRINT   = r'print'
    BREAK   = r'break'
    CONTINUE= r'continue'
    IF      = r'if'
    ELSE    = r'else'
    WHILE   = r'while'
    TRUE    = r'true'
    FALSE   = r'false'

    NAME = r'[a-zA-Z_][a-zA-Z_0-9]*'

    # Literals
    FLOAT = r'(\d+\.\d*|\.\d+)'
    INTEGER = r'\d+'
    CHAR = r"'([\s\S]|%s)'" % _escape_sequences

    @_(CHAR)
    def CHAR(self, token):
        token.value = token.value.replace("'", "")
        return token

# operators

    LE       = r'<='
    GE       = r'>='
    EQ       = r'=='
    NE       = r'!='
    LAND     = r'&&'
    LOR      = r'\|\|'
    PLUS     = r'\+'
    MINUS    = r'-'
    TIMES    = r'\*'
    DIVIDE   = r'/'
    LT       = r'<'
    GT       = r'>'
    LNOT     = r'!'
    ASSIGN   = r'='


# Miscellaneous Symbols

    SEMI     = r';'
    LPAREN   = r'\('
    RPAREN   = r'\)'
    LBRACE   = r'{'
    RBRACE   = r'}'
    DOT      = r'\.'

#     ignore = ' \t'

# High level function that takes input source text and turns it into tokens.
# This is a natural place to use some kind of generator function.

def tokenize(text):
    lexer = WabbitLexer()
    for tok in lexer.tokenize(text):
        yield tok

# Main program to test on input files
def main(filename=None, text=None):
    if text is None:
        with open(filename) as file:
            text = file.read()

    for tok in tokenize(text):
        print(tok)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        main(filename=sys.argv[1])
    else:
        main(text="abc 23 + 2 +")
