'''
Exercise R.5:
Write a recursive function that merges two sorted lists of numbers
into a single sorted list.
For example::

    >>> merge([1, 8, 9, 14, 15], [2, 10, 23])
    [1, 2, 8, 9, 10, 14, 15, 23]
'''


def merge(lst_1, lst_2):
    if not lst_1:
        return lst_2
    elif not lst_2:
        return lst_1

    if lst_1[0] < lst_2[0]:
        new_list = [lst_1[0]]
        new_list.extend(merge(lst_1[1:], lst_2))
    else:
        new_list = [lst_2[0]]
        new_list.extend(merge(lst_1, lst_2[1:]))
    return new_list


assert (merge([1, 8, 9, 14, 15], [2, 10, 23])
        == [1, 2, 8, 9, 10, 14, 15, 23])
