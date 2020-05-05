# q.py
#
# Writing a parser using tools (SLY)

from wabbit.tokenize import WabbitLexer
from sly import Parser
from wabbit.model import *

class WabbitParser(Parser):
    tokens = WabbitLexer.tokens        # Specifying all valid tokens

    # @_ is magically here via metaclasses. 

    #   token  method    token
    @_('PRINT expression SEMI')       # print_statment : PRINT expression SEMI
    def print_statement(self, p):
        return PrintStatement(p.expression)

    @_('INTEGER')
    def expression(self, p):
        return Integer(int(p.INTEGER))

    @_('FLOAT')
    def expression(self, p):
        return Float(float(p.FLOAT))
    
    @_('expression PLUS expression')
    def expression(self, p):
        return BinOp('+', p.expression0, p.expression1)




        
