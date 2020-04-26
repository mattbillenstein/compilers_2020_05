'''
Instructions
============

As input, a compiler needs to read source code.
To do this, it first has to recognize certain pattens in the code such
as names, number, operators, and so forth. This step is known as tokenizing.
Implement the following tokenize() function. It takes a string as input and
produces a sequence of tuples of the form (toktype, value) where toktype is a
token type and value is a string of the matching text::

    def tokenize(text):
        ...

    assert list(tokenize("spam = x + 34 * 567")) == \
        [ ('NAME', 'spam'), ('ASSIGN', '='), ('NAME', 'x'),
          ('OP', '+'), ('NUM', '34'),('OP', '*'), ('NUM', '567')]
'''

# Observations:

# 1) we are asked to write a function that produces a
# "sequence of tuple"; by sequence, I will assume a list.

# 2) The example given has tokens separated by single white spaces.
# The first example I will write will assume that this is always the case.


def tokenize(text):
    result = []
    tokens = text.split()
    for token in tokens:
        if token == "=":
            result.append(('ASSIGN', token))
        elif token in ("*", "+"):
            result.append(('OP', token))
        elif token[0].isdigit():
            result.append(('NUM', token))
        else:
            result.append(('NAME', token))
    return result


assert list(tokenize("spam = x + 34 * 567")) == \
    [('NAME', 'spam'), ('ASSIGN', '='), ('NAME', 'x'),
        ('OP', '+'), ('NUM', '34'), ('OP', '*'), ('NUM', '567')]

# In the tools section of the wiki, SLY is mentioned. SLY already includes
# its own tokenizer, but tokens must properly defined for it.
# To get familiear with using SLY, I will implement a second version using it.


def tokenize2(text):
    from sly import Lexer

    class ToyLexer(Lexer):
        # Weird Python construct where we include undefined symbols
        # in a set ...
        tokens = {NAME, NUM, OP, ASSIGN}

        # ... followed by their definitions here
        NAME = r'[a-zA-Z]+'
        NUM = r'\d+'
        OP = r'[\+\*]'
        ASSIGN = r'='

        ignore = ' \t'

    lexer = ToyLexer()
    result = []
    for token in lexer.tokenize(text):
        result.append((token.type, token.value))

    return result


assert list(tokenize2("spam = x + 34 * 567")) == \
    [('NAME', 'spam'), ('ASSIGN', '='), ('NAME', 'x'),
        ('OP', '+'), ('NUM', '34'), ('OP', '*'), ('NUM', '567')]
