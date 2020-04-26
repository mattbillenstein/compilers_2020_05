'''
Exercise R.4:
Write a recursive function that counts the number of occurrences of an
item in nested lists.
For example::

    >>> count_occurrences(2, [1, [4, [5, 2], 2], [8, [2, 9]]])
    3
'''


def count_occurrences(match, lst):
    count = 0
    for item in lst:
        if item == match:
            count += 1
        elif isinstance(item, list):
            count += count_occurrences(match, item)

    return count


assert count_occurrences(2, [1, [4, [5, 2], 2], [8, [2, 9]]]) == 3
