from .model import *
from .tokenize import tokenize, WabbitLexer

from sly import Parser

class WabbitParser(Parser):
    tokens = WabbitLexer.tokens
    precedence = (
        ('left', PLUS, MINUS)
        ('left', TIMES, DIVIDE)
        ('left', LT, LE, GT, GE, EQ, NE, LAND, LOR, LNOT)
    )
    
    def __init__(self):
        self.names = {}

    @_('statements')
    def program(self, p):
        return p[0]

    @_('{ statement }')
    def statements(self, p):
        return p.statement

    @_('print_statement',
       'assignment_statement',
       'variable_definition',
       'if_statement',
       'while_statement',
       'break_statement',
       'continue_statement',
       'expr',
       )
    def statement(self, p):
        return p[0]

    @_('PRINT expr SEMI')
    def print_statement(self, p):
        return PrintStatement(p.expr)

    @_('location ASSIGN expr SEMI')
    def assignment_statement(self, p):
        return AssignStatement(p.location, p.expr)

    @_('VAR NAME [ type ] [ ASSIGN expr ] SEMI')
    def variable_definition(self, p):
        return AssignStatement(DeclStorageLocation(p.NAME, p.type, False), p.expr)

    @_('CONST NAME [ type ] [ ASSIGN expr ] SEMI')
    def variable_definition(self, p):
        return AssignStatement(DeclStorageLocation(p.NAME, p.type, True), p.expr)

    @_('IF expr LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]')
    def while_statement(self, p):
        return ConditionalLoopStatement(p.expr, p.statements, p.statements)

    @_('CONTINUE SEMI')
    def continue_statement(self, p):
        return ContinueLoopStatement()

    @_('BREAK SEMI')
    def break_statement(self, p):
        return BreakLoopStatement()

    @_('expr PLUS expr',
       'expr MINUS expr',
       'expr TIMES expr',
       'expr DIVIDE expr',
       'expr LT expr',
       'expr LE expr',
       'expr GT expr',
       'expr GE expr',
       'expr EQ expr',
       'expr NE expr',
       'expr LAND expr',
       'expr LOR expr',
       'expr LNOT expr')
    def expr(self, p):
        return BinOp(p[1], p.expr0, p.expr1)

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr

    @_('PLUS expr',
       'MINUS expr',
       'LNOT expr')
    def expr(self, p):
        return UnOp(p[1], p.expr)

    @_('location')
    def expr(self, p):
        return NotImplementedError

    @_('literal')
    def expr(self, p):
        return NotImplementedError

    @_('LBRACE statements RBRACE')
    def expr(self, p):
        return BlockExpression(p.statements)

    @_('INTEGER')
    def literal(self, p):
        return Integer(p.INTEGER)

    @_('FLOAT')
    def literal(self, p):
        return Float(p.FLOAT)

    @_('CHAR')
    def literal(self, p):
        return Char(p.CHAR)

    @_('TRUE')
    def literal(self, p):
        return True

    @_('FALSE')
    def literal(self, p):
        return False

    @_('LPAREN RPAREN')
    def literal(self, p):
        return None

    @_('NAME')
    def location(self, p):
        return StorageLocation(p.NAME)

    @_('NAME')
    def type(self, p):
        return p.NAME

    @_('')
    def empty(self, p):
        pass


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


def parse_tokens(tokens):
    parser = WabbitParser()
    return parser.parse(tokens)


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        raise SystemExit('Usage: wabbit.parse filename')
    print(parse_file(sys.argv[1]))
