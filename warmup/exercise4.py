'''
Exercise 4: Tree simplification
===============================

Write a function that takes a tree and looks for places where
mathematical operations can be simplified.
A new simplified tree is returned::

def simplify_tree(tree):
    ...

tree = ('assign', 'spam',
        ('binop', '+',
                  ('name', 'x'),
                  ('binop', '*', ('num', 34), ('num', 567))))

assert simplify_tree(tree) == \
    ('assign', 'spam', ('binop', '+', ('name', 'x'), ('num', 19278)))
'''


def simplify_tree(tree):

    tok_type = tree[0]

    if tok_type == 'binop':
        # print("binop", tree)
        arg1 = tree[2]
        arg2 = tree[3]
        if arg1[0] == 'num' and arg2[0] == 'num':
            if tree[1] == '+':
                result = arg1[1] + arg2[1]
            elif tree[1] == '*':
                result = arg1[1] * arg2[1]
            return ('num', result)
        else:
            return ('binop', tree[1], simplify_tree(tree[2]),
                    simplify_tree(tree[3]))

    elif tok_type in ('num', 'name'):
        return tree
    elif tok_type == 'assign':
        if isinstance(tree[2], tuple):
            return (tree[0], tree[1], simplify_tree(tree[2]))
        else:
            return tree


tree = ('assign', 'spam',
        ('binop', '+',
                  ('name', 'x'),
                  ('binop', '*', ('num', 34), ('num', 567))))


assert (simplify_tree(tree) ==
        ('assign', 'spam', ('binop', '+', ('name', 'x'), ('num', 19278))))
