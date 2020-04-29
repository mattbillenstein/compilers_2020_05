#!/usr/bin/env python3

'''
# Recursion Exercises

One of the main challenges faced by participants in the compilers course is the heavy use of recursion.  Recursion is a natural part of compilers because most of the underlying data structures are trees.

To prepare, you might try writing some recursive functions using a programming language that you already know such as Python.  Here is an example of counting over a range of numbers using recursion:
'''

def count(start, stop):
    if start >= stop:
        return
    else:
        print(start)
        count(start+1, stop)

# Count from 0 to 9
#count(0, 10)

'''
Here is a classic example that computes factorials:
'''

def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)

'''
## Exercises

Here are some additional exercises you can try.  Again, do these in
Python or some other familiar language.

### Exercise R.1:

Write a recursive function `count_multiples(a, b)` 
that counts how many multiples of `a` are part of the
factorization of the number `b`. For example:
'''

def count_multiples(fact, num):
    if num % fact == 0:
        return 1 + count_multiples(fact, num // fact)
    return 0

assert count_multiples(2, 6) == 1    # 2 * 3 = 6
1
assert count_multiples(2, 12) == 2   # 2 * 2 * 3 = 12
2
assert count_multiples(3, 11664) == 6

'''
### Exercise R.2:

Write a recursive function that finds the maximum
value in a Python list without using any kind of
looping construct such as "for" or "while."

Hint: You may use slices.

For example:
'''

def maxval(L):
    if len(L) == 1:
        return L[0]

    i = len(L) // 2
    a, b = maxval(L[:i]), maxval(L[i:])
    if a > b:
        return a
    return b

assert maxval([1, 9, -3, 7, 13, 2, 3]) == 13

'''
### Exercise R.3:

Write a recursive function that flattens nested Python lists. For example:
'''

def flatten(o):
    if not isinstance(o, list):
        return [o]

    # empty list
    if not o:
        return o

    return flatten(o[0]) + flatten(o[1:])

assert flatten([1, [2, [3, 4], 5], 6]) == [1, 2, 3, 4, 5, 6]

'''
### Exercise R.4:

Write a recursive function that counts the number of 
occurrences of an item in nested lists. For example:
'''

def count_occurrences(num, L):
    # cute
    # return flatten(L).count(num)

    if not isinstance(L, list):
        return 1 if L == num else 0

    # empty list
    if not L:
        return 0

    return count_occurrences(num, L[0]) + count_occurrences(num, L[1:])

assert count_occurrences(2, [1, [4, [5, 2], 2], [8, [2, 9]]]) == 3

'''
### Exercise R.5:

Write a recursive function that merges two sorted lists of numbers
into a single sorted list. For example:
'''

def merge(L1, L2):
    if not L1:
        return L2
    if not L2:
        return L1
    if L2[0] < L1[0]:
        L2, L1 = L1, L2
    return L1[0:1] + merge(L1[1:], L2)

assert merge([1, 8, 9, 14, 15], [2, 10, 23]) == [1, 2, 8, 9, 10, 14, 15, 23]

'''
### Exercise R.6:

Write a recursive function that reverses a linked-list constructed from
Python 2-tuples. For example:
'''

# mattb - is there a way to do this without a second optional argument?  ie,
# extra storage other than the call stack?
def reverse(tup, head=None):
    if tup:
        return reverse(tup[1], (tup[0], head))
    return head

assert reverse((1, (2, (3, (4, None))))) == (4, (3, (2, (1, None))))

'''
## Important Note

The above exercises are only meant for recursion practice. Some are
more difficult than others, but none are essential for ultimate success in writing
a compiler.
'''
