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

    tok_type, *args = tree

    if tok_type in ('num', 'name'):
        return tree

    elif tok_type == 'assign':
        name, rest = args
        return ('assign', name, simplify_tree(rest))

    elif tok_type == 'binop':
        op, left, right = args
        left_type, left_value = left = simplify_tree(left)
        right_type, right_value = right = simplify_tree(right)

        if left_type == 'num' and right_type == 'num':
            if op == '+':
                result = left_value + right_value
            elif op == '*':
                result = left_value * right_value
            return ('num', result)
        else:
            return ('binop', op, left, right)


tree = ('assign', 'spam',
        ('binop', '+',
                  ('name', 'x'),
                  ('binop', '*', ('num', 34), ('num', 567))))

assert (simplify_tree(tree) ==
        ('assign', 'spam', ('binop', '+', ('name', 'x'), ('num', 19278))))


# More complicated case where recursion is actually needed

tree = ('assign', 'spam',
        ('binop', '+',
                  ('num', 3),
                  ('binop', '*', ('num', 4), ('num', 5))))

assert simplify_tree(tree) == ('assign', 'spam', ('num', 23))
