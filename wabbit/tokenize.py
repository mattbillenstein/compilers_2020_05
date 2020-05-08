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

    tokens = {

    # Reserved keywords
    CONST, VAR, PRINT, BREAK, CONTINUE, IF, ELSE, WHILE, TRUE, FALSE,

    # Identifiers
    NAME,

    # Literals: numbers and characters
    FLOAT, INTEGER, CHAR,

    # Operators
    LE, GE, EQ, NE, LAND, LOR, PLUS, MINUS, TIMES, DIVIDE, LT, GT, LNOT, ASSIGN,

    # Miscellaneous symbols
     SEMI, LPAREN, RPAREN, LBRACE, RBRACE, DOT
    }

    ignore = ' \t'       # Characters ignored between tokens

    @_('\n+')
    def ignore_newline(self, tok):
        self.lineno += tok.value.count('\n')

    @_(r'/\*(.|\n)*?\*/')
    def ignore_block_comment(self, tok):
        self.lineno += tok.value.count('\n')

    ignore_line_comment = r'//.*'


# Identifiers
    NAME = r'[a-zA-Z_][a-zA-Z_0-9]*'

# If we were to identify keywords with a regular expresion, something like:
#   CONST = r'const'
# then, it could mistakenly match parts of a word, like 'constant'.
# Instead, we wish to identify keywords as a complete word; here's how
# to do it with sly, as a special case of the above.

# Reserved keywords:
    NAME['const'] = CONST
    NAME['var'] = VAR
    NAME['print'] = PRINT
    NAME['if'] = IF
    NAME['else'] = ELSE
    NAME['while'] = WHILE
    NAME['break'] = BREAK
    NAME['continue'] = CONTINUE
    NAME['true'] = TRUE
    NAME['false'] = FALSE


# Literals: numbers and characters
    FLOAT = r'(\d+\.\d*|\.\d+)'
    INTEGER = r'\d+'

    # The following is adopted from Spencer
    _escape_sequences = "|".join([
        r'\\\\',
        r"\\'",
        r'\\\"',
        r'\\[abfnrtv]',
        r'\\\d{1,3}',
        r'\\x[a-fA-F0-9]{1,2}',
    ])
    CHAR = r"'([\s\S]|%s)'" % _escape_sequences

    @_(CHAR)
    def CHAR(self, token):
        token.value = token.value.replace("'", "")
        return token

# Operators; we need to put the longer operators first to avoid
# identifying parts of an operator as a different one.
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


# Miscellaneous symbols
    SEMI     = r';'
    LPAREN   = r'\('
    RPAREN   = r'\)'
    LBRACE   = r'{'
    RBRACE   = r'}'
    DOT      = r'\.'


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
