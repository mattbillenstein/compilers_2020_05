'''
Exercise 2: Trees
=================

Inside a compiler, source code is usually represented by some sort of
tree structure. Trees are usually recursive in nature--as are the algorithms
dealing with the data.
Write a Python function that takes a tree structure and converts into a
string representing source code::

    def to_source(tree):
        ...

    tree = ('assign', 'spam',
            ('binop', '+',
                      ('name', 'x'),
                      ('binop', '*', ('num', '34'), ('num', '567'))))

    assert to_source(tree) == 'spam = x + 34 * 567'
'''


def to_source(tree):
    result = []
    tok_type = tree[0]
    if tok_type == 'assign':
        result.append(tree[1])
        result.append('=')
        result.append(to_source(tree[2]))
    elif tok_type == 'binop':
        result.append(to_source(tree[2]))
        result.append(tree[1])
        result.append(to_source(tree[3]))
    elif tok_type in ('name', 'num'):
        result.append(tree[1])
    else:
        print("This should not happen")

    return ' '.join(result)


tree = ('assign', 'spam',
        ('binop', '+',
                  ('name', 'x'),
                  ('binop', '*', ('num', '34'), ('num', '567'))))

assert to_source(tree) == 'spam = x + 34 * 567'
