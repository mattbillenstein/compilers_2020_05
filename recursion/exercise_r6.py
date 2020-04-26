'''
Exercise R.6:
Write a recursive function that reverses a linked-list constructed from
Python 2-tuples.
For example::

    >>> reverse((1, (2, (3, (4, None)))))
    (4, (3, (2, (1, None))))
'''


def reverse(original, reversed=None):
    # print(original, reversed)
    if original is None:
        return reversed
    item, tup = original
    return reverse(tup, reversed=(item, reversed))


assert reverse((1, (2, (3, (4, None))))) == (4, (3, (2, (1, None))))
