# fact.py

def fact(n):
    r = 1
    while n > 0:
        r *= n
        n -= 1
    return r
