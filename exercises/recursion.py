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
