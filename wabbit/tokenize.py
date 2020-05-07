# tokenizer.py
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

import os.path

import sly


class WabbitLexer(sly.Lexer):
    # few regexs stolen from dabeaz in the interest of time...
    # CHAR, comments

    _binop = {
        LE, GE, EQ, NE, LAND, LOR, LT, GT, PLUS, MINUS, TIMES, DIVIDE,
    }

    _unaop = { PLUS, MINUS, LNOT }

    _kw = {
        CONST, VAR, PRINT, BREAK,
        CONTINUE, IF, ELSE, WHILE, TRUE, FALSE,
        FUNC, RETURN,
    }

    tokens = {
        NAME, FLOAT, INTEGER, CHAR,
        ASSIGN, LPAREN, RPAREN, SEMI, LBRACE, RBRACE, DOT, COMMA, COLONCOLON,
    } | _unaop | _binop | _kw

    ignore = ' \t'

    ignore_line_comment = r'//.*'

    @_('\n+')
    def ignore_newline(self, tok):
        self.lineno += tok.value.count('\n')

    @_(r'/\*(.|\n)*?\*/')
    def ignore_block_comment(self, tok):
        self.lineno += tok.value.count('\n')

    # Tokens
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    FLOAT = r'(?:\d+\.\d*)|(?:\d*\.\d+)'
    INTEGER = r'\d+'
    CHAR = r"'(\\'|.)*?'"

    def CHAR(self, t):
        # emit escaped without quotes so we can reconstruct in to_source
        t.value = t.value[1:-1]
        return t

    # keywords
    NAME['const'] = CONST
    NAME['var'] = VAR
    NAME['print'] = PRINT
    NAME['break'] = BREAK
    NAME['continue'] = CONTINUE
    NAME['if'] = IF
    NAME['else'] = ELSE
    NAME['while'] = WHILE
    NAME['true'] = TRUE
    NAME['false'] = FALSE
    NAME['func'] = FUNC
    NAME['return'] = RETURN

    # Special symbols - multiple characters first!
    LE = r'<='
    GE = r'>='
    EQ = r'=='
    NE = r'!='
    LAND = r'&&'
    LOR = r'\|\|'
    COLONCOLON = r'::'
    LT = r'<'
    GT = r'>'
    LNOT = r'!'
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    ASSIGN = r'='
    LPAREN = r'\('
    RPAREN = r'\)'
    SEMI = r';'
    LBRACE = r'\{'
    RBRACE = r'\}'
    DOT = r'\.'
    COMMA = r','

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1


# High level function that takes input source text and turns it into tokens.
# This is a natural place to use some kind of generator function.

def tokenize(text):
    lexer = WabbitLexer()
    for tok in lexer.tokenize(text):
        yield tok

# Main program to test on input files
def main(args):
    if args:
        if os.path.isfile(args[0]):
            with open(args[0]) as file:
                text = file.read()
        else:
            text = args[0]
    else:
        text = sys.stdin.read()

    for tok in tokenize(text):
        print(tok)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
