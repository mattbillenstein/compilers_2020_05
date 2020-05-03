# func_models.py
#
# The WabbitFunc language extends WabbitScript with support for
# user-defined functions.  This requires additional support
# for the following constructs:
#
#     1. Function definitions.
#     2. Function application.
#     3. The return statement.
# 
# This file contains a single example that you should represent
# using your model.  Please see the following document for more information.
#
# https://github.com/dabeaz/compilers_2020_05/wiki/WabbitFunc.md

from wabbit.model import *

# ----------------------------------------------------------------------
# Program 6: Functions.  The program prints out the first factorials
# with various function definitions.
#

source6 = '''
func add(x int, y int) int {
    return x + y;
}

func mul(x int, y int) int {
    return x * y;
}

func factorial(n int) int {
    if n == 0 {
        return 1;
    } else {
        return mul(n, factorial(add(n, -1)));
    }
}

func print_factorials(last int) {
    var x = 0;
    while x < last {
        print factorial(x);
        x = add(x, 1);
}

func main() int {
    var result = print_factorials(10);
    return 0;
}
'''

model6 = None

# print(to_source(model6))

# ----------------------------------------------------------------------
# Bring it!  If you're here wanting even more, proceed to the file 
# "type_models.py".
