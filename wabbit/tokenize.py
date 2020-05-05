# tokenizer.py
#
# The role of a tokenizer is to turn raw text into recognized symbols 
# known as tokens. 

from sly import Lexer


class WabbitLexer(Lexer):
    tokens = { IDENTIFIER, CONST, VAR, PRINT, BREAK, CONTINUE, IF, ELSE, WHILE, TRUE, FALSE, INTEGER, FLOAT, CHAR,
            PLUS, MINUS, TIMES, DIVIDE, LTE, LT, GTE, GT, EQ, NE, LAND, LOR, LNOT, ASSIGN, SEMI, LPAREN, RPAREN,
            LBRACE, RBRACE}
    ignore = ' \t\n'
    ignore_multilinecomments = r'\/\*[^*]*\*+(?:[^/*][^*]*\*+)*\/'
    ignore_midlinecomments = r'\/\/.*'

    IDENTIFIER = r'[A-Za-z_][A-Za-z0-9_]*'
    CONST = r'const'
    VAR = r'var'
    PRINT = r'print'
    BREAK = r'break'
    CONTINUE = r'continue'
    IF = r'if'
    ELSE = r'else'
    WHILE = r'while'
    TRUE = r'true'
    FALSE = r'false'

    INTEGER = r'[0-9]+'
    FLOAT = r'[0-9]*\.[0-9]*'
    CHAR = r"'(\'|\n|[a-z][A-Z][0-9]|\\x[0-9]{2})'"

    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    LTE = r'<='
    LT = r'<'
    GTE = r'>='
    GT = r'>'
    EQ = r'=='
    NE = r'!='
    LAND = r'&&'
    LOR = r'\|\|'
    LNOT = r'!'

    ASSIGN = r'='
    SEMI = r';'
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACE = r'{'
    RBRACE = r'}'


def tokenize(text):
    ...
    yield tok
    ...


if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    lexer = WabbitLexer()
    with open(filename) as file:
        text = file.read()
    for tok in lexer.tokenize(text):
        print(tok)
