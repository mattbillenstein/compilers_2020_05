'''
Exercise R.3:
Write a recursive function that flattens nested Python lists.
For example::

    >>> flatten([1, [2, [3, 4], 5], 6])
    [1, 2, 3, 4, 5, 6]
'''


def flatten(lst):
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


assert flatten([1, [2, [3, 4], 5], 6]) == [1, 2, 3, 4, 5, 6]

# More complex test
assert (flatten([1, [4, [[5, 2]], 2], [8, [2, 9]], [0]]) ==
        [1, 4, 5, 2, 2, 8, 2, 9, 0])
