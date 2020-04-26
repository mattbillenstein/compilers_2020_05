'''
Exercise 3: Tree rewriting
==========================

Write a function that takes a tree of text strings as input and
creates a new tree where all of the numbers have been converted to integers::

    def convert_numbers(tree):
        ...

    tree = ('assign', 'spam',
            ('binop', '+',
                      ('name', 'x'),
                      ('binop', '*', ('num', '34'), ('num', '567'))))

assert convert_numbers(tree) == \
    ('assign', 'spam', ('binop', '+', ('name', 'x'),
    ('binop', '*', ('num', 34), ('num', 567))
'''


def convert_numbers(tree):
    new_tree = []
    for item in tree:
        if isinstance(item, tuple):
            new_tree.append(convert_numbers(item))
        elif item.isdigit():
            new_tree.append(int(item))
        else:
            new_tree.append(item)
    return tuple(new_tree)


tree = ('assign', 'spam',
        ('binop', '+',
                  ('name', 'x'),
                  ('binop', '*', ('num', '34'), ('num', '567'))))

new_tree = ('assign', 'spam',
            ('binop', '+',
                      ('name', 'x'),
                      ('binop', '*', ('num', 34), ('num', 567))))

assert convert_numbers(tree) == new_tree
