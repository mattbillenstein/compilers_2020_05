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


class TokenVisitor():
    def __init__(self):
        raise NotImplementedError

    def visit_IDENTIFIER(self, node):
        raise NotImplementedError

    def visit_CONST(self, node):
        raise NotImplementedError

    def visit_VAR(self, node):
        raise NotImplementedError

    def visit_PRINT(self, node):
        raise NotImplementedError

    def visit_BREAK(self, node):
        raise NotImplementedError

    def visit_CONTINUE(self, node):
        raise NotImplementedError

    def visit_IF(self, node):
        raise NotImplementedError

    def visit_ELSE(self, node):
        raise NotImplementedError

    def visit_WHILE(self, node):
        raise NotImplementedError

    def visit_TRUE(self, node):
        raise NotImplementedError

    def visit_FALSE(self, node):
        raise NotImplementedError

    def visit_INTEGER(self, node):
        raise NotImplementedError

    def visit_FLOAT(self, node):
        raise NotImplementedError

    def visit_CHAR(self, node):
        raise NotImplementedError

    def visit_PLUS(self, node):
        raise NotImplementedError

    def visit_MINUS(self, node):
        raise NotImplementedError

    def visit_TIMES(self, node):
        raise NotImplementedError

    def visit_DIVIDE(self, node):
        raise NotImplementedError

    def visit_LE(self, node):
        raise NotImplementedError

    def visit_LT(self, node):
        raise NotImplementedError

    def visit_GE(self, node):
        raise NotImplementedError

    def visit_GT(self, node):
        raise NotImplementedError

    def visit_EQ(self, node):
        raise NotImplementedError

    def visit_NE(self, node):
        raise NotImplementedError

    def visit_LAND(self, node):
        raise NotImplementedError

    def visit_LOR(self, node):
        raise NotImplementedError

    def visit_LNOT(self, node):
        raise NotImplementedError

    def visit_ASSIGN(self, node):
        raise NotImplementedError

    def visit_SEMI(self, node):
        pass

    def visit_LPAREN(self, node):
        raise NotImplementedError

    def visit_RPAREN(self, node):
        raise NotImplementedError
    
    def visit_LBRACE(self, node):
        raise NotImplementedError
    
    def visit_RBRACE(self, node):
        raise NotImplementedError
