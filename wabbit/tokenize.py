from sly import Lexer
from sly.lex import Token


class Token(Token):
    '''
    Representation of a single token.
    '''
    __slots__ = ('type', 'value', 'lineno', 'index')
    def __init__(self, type, value, lineno, index):
        self.type = type
        self.value = value
        self.lineno = lineno
        self.index = index

    def __eq__(self, other):
        return other.__class__.__name__ == 'Token' and \
               self.type == other.type and \
               self.value == other.value and \
               self.lineno == other.lineno and \
               self.index == other.index


class WabbitLexer(Lexer):
    tokens = { NAME, CONST, VAR, PRINT, BREAK, CONTINUE, IF, ELSE, WHILE, TRUE, FALSE, INTEGER, FLOAT, CHAR,
            PLUS, MINUS, TIMES, DIVIDE, LE, LT, GE, GT, EQ, NE, LAND, LOR, LNOT, ASSIGN, SEMI, LPAREN, RPAREN,
            LBRACE, RBRACE}
    ignore = ' \t\n'
    ignore_multilinecomments = r'\/\*[^*]*\*+(?:[^/*][^*]*\*+)*\/'
    ignore_midlinecomments = r'\/\/.*'

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
    NAME = r'[A-Za-z_][A-Za-z0-9_]*'

    FLOAT = r'[0-9]*\.[0-9]*'
    INTEGER = r'[0-9]+'
    CHAR = r"'(\'|\n|[a-z][A-Z][0-9]|\\x[0-9]{2})'"

    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    LE = r'<='
    LT = r'<'
    GE = r'>='
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


def to_tokens(text):
    lexer = WabbitLexer()
    return lexer.tokenize(text)


if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    lexer = WabbitLexer()
    with open(filename) as file:
        text = file.read()
    for tok in lexer.tokenize(text):
        print(tok)
