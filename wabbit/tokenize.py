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

from sly import Lexer      # Disclaimer: I created SLY

class WabbitLexer(Lexer):
    # Valid token names
    tokens = { 
        # Operators 
        PLUS, MINUS, TIMES, DIVIDE, LT, LE, GT, GE, EQ, NE, LAND, LOR, LNOT,
          
        # Other symbols
        ASSIGN, LPAREN, RPAREN, LBRACE, RBRACE, SEMI, DOT, 

        # Numbers and characters
        INTEGER, FLOAT, CHAR,

        # Identifiers
        NAME,

        # Special keywords
        CONST, VAR, PRINT, IF, WHILE, ELSE, CONTINUE, BREAK, TRUE, FALSE,
        }

    ignore = ' \t'       # Ignore these (between tokens)

    @_('\n+')
    def ignore_newline(self, tok):
        self.lineno += tok.value.count('\n')

    @_(r'/\*(.|\n)*?\*/')
    def ignore_block_comment(self, tok):
        self.lineno += tok.value.count('\n')
    
    ignore_line_comment = r'//.*'

    # Numbers
    FLOAT = r'(\d+\.\d*)|(\d*\.\d+)'
    INTEGER = r'\d+'

    # Names/Identifiers
    # PRINT = 'print'     # BAD IDEA.  Matches other words that start with "print"

    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'    # Variable name

    # These are special cases. If the matched text for NAME exactly matches the supplied string
    # the token type is changed to the value on the right
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

    # Character constants.   'x', '\'', '\n', '\xhh'.  Hard because of escape codes.
    CHAR = r"'(\\'|.)*?'"    # This matches any group of characters in-between '...' 
                             # as well as an escaped \'.  

    # Specify tokens as regex rules
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    DOT = r'\.'

    # Put longer patterns first
    LE = r'<='
    LT = r'<'               # Order matters a lot. Definition order is the order matches are tried.
    GE = r'>='
    GT = r'>'
    EQ = r'=='
    NE = r'!='
    LAND = r'\&\&'
    LOR = r'\|\|'
    LNOT = r'!'
    ASSIGN = r'='
    SEMI = r';'
    LPAREN =r'\('
    RPAREN = r'\)'
    LBRACE = r'{'
    RBRACE = r'}'

    def error(self, tok):
        # Error function.  Called on illegal characters
        print(f'Illegal character {tok.value[0]!r}')
        self.index += 1     # Skip ahead one character

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

    
            
        

            
    
