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
# Sample:
#
# for tok in tokenize("print 2 + 3 * 4;"):
#     print(tok)
#

# Tokenizing is based solved.  Not interesting.
# Tools available.

from sly import Lexer  # Disclaimer: I created SLY


class WabbitLexer(Lexer):
    # Valid token names
    tokens = {
        PLUS,
        MINUS,
        TIMES,
        DIVIDE,
        NUMBER,
        LT,
        LE,
        EQ,
        DECIMAL,
        GT,
        GE,
        EQ,
        NE,
        ASSIGN,
        LPAREN,
        RPAREN,
        LBRACE,
        RBRACE,
        SEMI,
    }
    ignore = " \t\n"  # Ignore these (between tokens)

    # Specify tokens as regex rules
    PLUS = r"\+"
    MINUS = r"-"
    TIMES = r"\*"
    DIVIDE = r"/"
    DECIMAL = r"\d+\.\d+"  # 23.45
    NUMBER = r"\d+"

    # Put longer patterns first
    LE = r"<="
    LT = r"<"  # Order matters a lot. Definition order is the order matches are tried.
    GE = r">="
    GT = r">"
    EQ = r"=="
    NE = r"!="
    ASSIGN = r"="
    SEMI = r";"
    LPAREN = r"\("
    RPAREN = r"\)"
    LBRACE = r"{"
    RBRACE = r"}"


def tokenize(text):
    lexer = WabbitLexer()
    return lexer.tokenize(text)


# Main program to test on input files
def main(filename):
    with open(filename) as file:
        text = file.read()

    for tok in tokenize(text):
        print(tok)


if __name__ == "__main__":
    import sys

    main(sys.argv[1])

