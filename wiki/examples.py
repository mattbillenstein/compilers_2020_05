#!/usr/bin/env python3

'''
# Write a Compiler - Preparation Exercises

The following exercises are meant as a bit of warmup for the compiler
project. Don't spend tons of time on these, but coding a solution will
start to prepare you for the proper mindset.

## Exercise 1: Tokenizing

As input, a compiler needs to read source code.  To do this, it first has to
recognize certain pattens in the code such as names, number,
operators, and so forth.  This step is known as tokenizing.   Implement
the following `tokenize()` function.  It takes a string as input
and produces a sequence of tuples of the form `(toktype, value)`
where `toktype` is a token type and `value` is a string of
the matching text:

'''

import string

def tokenize(text):
    tokens = []

    ops = ['=', '+', '*']
    ws = [' ', '\t']
    nums = '0123456789'
    names = string.ascii_letters + '_'

    type = token = None

    for c in text:
        if c in ws:
            if token:
                tokens.append((type, token))
                token = type = None
            continue

        if c in ops:
            if token:
                tokens.append((type, token))
                type = token = None
            tokens.append(('ASSIGN' if c == '=' else 'OP', c))

        elif c in nums:
            # if we find a num, but we're already in a name, consider it part
            # of the name...
            if token and type in ('NUM', 'NAME'):
                token += c
            else:
                if token:
                    tokens.append((type, token))
                type, token = 'NUM', c

        elif c in names:
            if token:
                token += c
            else:
                type, token = 'NAME', c

        else:
            assert 0, f'Unknown character {c}'

    if token:
        tokens.append((type, token))
        type = token = None

    return tokens

assert list(tokenize("spam12_345 = x + 34 * 567")) == \
    [ ('NAME', 'spam12_345'), ('ASSIGN', '='), ('NAME', 'x'), 
      ('OP', '+'), ('NUM', '34'),('OP', '*'), ('NUM', '567')]

'''
## Exercise 2: Trees

Inside a compiler, source code is usually represented by some sort of tree
structure.  Trees are usually recursive in nature--as are the algorithms
for dealing with the data.   Write a Python function that takes a tree
structure and converts into a string representing source code:

'''

def to_source(tree):
    if tree[0] == 'assign':
        return f'{tree[1]} = {to_source(tree[2])}'
    elif tree[0] == 'binop':
        return f'{to_source(tree[2])} {tree[1]} {to_source(tree[3])}'
    elif tree[0] in ('name', 'num'):
        return f'{tree[1]}'
    else:
        assert 0, f'Unhandled node type {tree[0]}'

tree = ('assign', 'spam', 
            ('binop', '+',
                  ('name', 'x'),
                  ('binop', '*', ('num', '34'), ('num', '567'))))

assert to_source(tree) == 'spam = x + 34 * 567'

'''
## Exercise 3: Tree rewriting

Write a function that takes a tree of text strings as input and
creates a new tree where all of the numbers have been converted
to integers:

'''

def convert_numbers(tree):
    pass

tree = ('assign', 'spam', 
        ('binop', '+', 
                  ('name', 'x'),
                  ('binop', '*', ('num', '34'), ('num', '567'))))

assert convert_numbers(tree) == \
    ('assign', 'spam', ('binop', '+', ('name', 'x'), ('binop', '*', ('num', 34), ('num', 567))))    

'''
## Exercise 4: Tree simplification

Write a function that takes a tree and looks for places where mathematical
operations can be simplified.  A new simplified tree is returned:

'''

def simplify_tree(tree):
    pass

tree = ('assign', 'spam', 
        ('binop', '+', 
                  ('name', 'x'),
                  ('binop', '*', ('num', 34), ('num', 567))))

assert simplify_tree(tree) == \
    ('assign', 'spam', ('binop', '+', ('name', 'x'), ('num', 19278)))
