cdef inline int printdouble(double f):
    print("{:.6f}".format(f))
    return 0

cdef inline int printint(int i):
    print(i)
    return 0

cdef inline int printchar(str s):
    print(s, end="")


cdef inline int printbool(bint b):
    if b == 1:
        print("true")
    else:
        print("false")


cdef inline wabbitprint(s):
    if isinstance(s, float):
        printdouble(s)
    elif isinstance(s, bool):
        printbool(s)
    elif isinstance(s, int):
        printint(s)
    else:
        printchar(s)

#
# cdef extern from *:
#     """
#
#     /* This is C code which will be put
#      * in the .c file output by Cython */
#     #define wabbitprint(X) _Generic((X),        \\
#                            double: printdouble, \\
#                            int: printint,       \\
#                            str: printchar,       \\
#                            default: printchar    \\
#                            )(X)                  \\
#     """

cdef inline wabbitmatch(enum, patterns):
    return patterns.get(enum.choice)(enum.value)

cdef inline wabbit_divide(a, b):
    if isinstance(a, int) and isinstance(b, int):
        return <int>(a / b)

    elif isinstance(a, float) or isinstance(b, float):
        return a / b
    else:
        raise RuntimeError(f'Cannot divide objects of type "{type(a)}" and "{type(b)}"')

