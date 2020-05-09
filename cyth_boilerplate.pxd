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


cdef inline wabbitprint(s):
    if isinstance(s, float):
        printdouble(s)
    elif isinstance(s, bool):
        printbool(s)
    elif isinstance(s, int):
        printint(s)
    else:
        printchar(s)