def count_multiples(a: int, b: int):
    """
    Count how many multiples of a are part of the factorization of b.

    >>> count_multiples(2, 6)     # 2 * 3 = 6
    1
    >>> count_multiples(2, 12)    # 2 * 2 * 3 = 12
    2
    >>> count_multiples(3, 11664)
    6
    """
    quot, rem = divmod(b, a)
    if rem:
        return 0
    else:
        return 1 + count_multiples(a, quot)


def maxval(x: list):
    """
    Find the maximum value in a Python list without using any kind of looping construct such
    as "for" or "while."

    >>> maxval([1, 9, -3, 7, 13, 2, 3])
    13
    """
    return x[0] if len(x) == 1 else max(x[0], maxval(x[1:]))


def flatten(x):
    """
    >>> flatten([1, [2, [3, 4], 5], 6])
    [1, 2, 3, 4, 5, 6]
    """
    # It seems that if this is a single function then it must accept either an atom or a list.
    # (Unlike maxval)
    if isinstance(x, list):
        # TODO: why is this different from the lisp implementation?
        if not x:
            return x
        else:
            return flatten(x[0]) + flatten(x[1:])
    else:
        return [x]


def count_occurrences(a, x):
    """
    >>> count_occurrences(2, [1, [4, [5, 2], 2], [8, [2, 9]]])
    3
    """
    if isinstance(x, list):
        # TODO: why is this different from the lisp implementation?
        if not x:
            return 0
        else:
            return count_occurrences(a, x[0]) + count_occurrences(a, x[1:])
    else:
        return int(x == a)


def merge(x, y):
    """
    >>> merge([1, 8, 9, 14, 15], [2, 10, 23])
    [1, 2, 8, 9, 10, 14, 15, 23]
    """
    if not x:
        return y
    if not y:
        return x
    if x[0] < y[0]:
        return x[:1] + merge(x[1:], y)
    else:
        return y[:1] + merge(x, y[1:])
