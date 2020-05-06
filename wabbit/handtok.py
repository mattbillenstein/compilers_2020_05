# handtok.py
#
# Hand-written Wabbit tokenizer.  No Tools.
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

class Token:
    def __init__(self, type, value, lineno):
        self.type = type
        self.value = value
        self.lineno = lineno

    def __repr__(self):
        return f'Token({self.type!r}, {self.value!r}, {self.lineno})'


# Two-character operators/symbols
_two_char = {
    '==': 'EQ',
    '!=': 'NE',
    '<=': 'LE',
    '>=': 'GE',
    '&&': 'LAND',
    '||': 'LOR',
}

# Single-character operators/symbols
_one_char = {
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'TIMES',
    '/': 'DIVIDE',
    '<': 'LT',
    '>': 'GT',
    '=': 'ASSIGN',
    '(': 'LPAREN',
    ')': 'RPAREN',
    '{': 'LBRACE',
    '}': 'RBRACE',
    ';': 'SEMI',
    '!': 'LNOT',
}

# Keywords
_keywords = {'const', 'var', 'print', 'if', 'else', 'while', 'break', 'continue', 'true', 'false'}


def tokenize(text):
    n = 0
    lineno = 1
    while n < len(text):
        if text[n] == '\n':
            lineno += 1
            n += 1
            continue

        # Skip whitespace between tokens
        if text[n].isspace():
            n += 1;
            continue

        # Check for a comment.  /* .... bunch of random stuff ... */
        if text[n:n + 2] == '/*':
            end = text.find("*/", n + 2)
            if end < 0:
                print("Unterminated comment")
                return
            lineno += text[n:end].count('\n')
            n = end + 2
            continue

        # Check for a // comment
        if text[n:n + 2] == '//':
            end = text.find('\n', n + 2)
            if end < 0:
                return
            lineno += 1
            n = end + 1
            continue

        # Look for two-character tokens
        if text[n:n + 2] in _two_char:
            val = text[n:n + 2]
            yield Token(_two_char[val], val, lineno)
            n += 2
            continue

        # Look for rone-character tokens
        if text[n] in _one_char:
            val = text[n]
            yield Token(_one_char[val], val, lineno)
            n += 1
            continue

        # Check for numbers
        if text[n].isdigit():
            start = n
            while n < len(text) and text[n].isdigit():
                n += 1
            if n < len(text) and text[n] == '.':
                n += 1
                while n < len(text) and text[n].isdigit():
                    n += 1
                yield Token('FLOAT', text[start:n], lineno)
            else:
                yield Token('INT', text[start:n], lineno)
            continue

        # Check for names/identifiers
        if text[n].isalpha() or text[n] == '_':
            start = n
            while n < len(text) and (
                    text[n].isalpha() or
                    text[n].isdigit() or
                    text[n] == '_'):
                n += 1
            val = text[start:n]
            if val in _keywords:
                yield Token(val.upper(), val, lineno)
            else:
                yield Token('ID', val, lineno)
            continue

        # Check for characters
        if text[n] == "'":
            start = n
            n += 1
            while n < len(text) and text[n] != "'":
                if text[n] == '\\':
                    n += 1  # Just consume the next character if escape
                n += 1
            val = text[start:n + 1]
            yield Token('CHAR', val, lineno)
            n += 1
            continue

        print("Illegal character {text[n]!r}")
        n += 1


# Main program to test on input files
def main(filename):
    with open(filename) as file:
        text = file.read()

    for tok in tokenize(text):
        print(tok)


if __name__ == '__main__':
    import sys

    main(sys.argv[1])