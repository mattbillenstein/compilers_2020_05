'''
Exercise R.2:
Write a recursive function that finds the maximum value in a Python list
without using any kind of looping construct such as "for" or "while."
For example::

    >>> maxval([1, 9, -3, 7, 13, 2, 3])
    13
    >>>

Hint: You may use slices.
'''


def maxval(lst, max_=None):
    if max_ is None:
        max_ = lst[0]  # ignore empty lists
    if not lst[1:]:
        return max_
    max_ = max(max_, lst[0])
    return max(max_, maxval(lst[1:], max_))


assert maxval([1, 9, -3, 7, 13, 2, 3]) == 13
