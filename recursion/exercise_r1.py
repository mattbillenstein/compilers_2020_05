'''Recursion exercise R.1

Write a recursive function count_multiples(a, b) that counts
how many multiples of a are part of the factorization of the number b.
For example::

    >>> count_multiples(2, 6)     # 2 * 3 = 6
    1
    >>> count_multiples(2, 12)    # 2 * 2 * 3 = 12
    2
    >>> count_multiples(3, 11664)
    6

'''


def count_multiples(factor, number):
    count = 0

    divide = number // factor
    if factor * divide == number:
        count = 1
        count += count_multiples(factor, divide)

    return count


assert count_multiples(2, 6) == 1
assert count_multiples(2, 12) == 2
assert count_multiples(3, 11664) == 6

assert count_multiples(2, 1024) == 10
