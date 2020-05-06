
from wabbit.parse import parse_source

#     print 1;
#     print 2.5;
#
# From there, expand it to handle expressions:
#
#     print 2 + 3 * -4;
#
# Then, expand it to include variable names
#
#     var x = 3;
#     print 2 + x;

# print('prelim', 1)
# s = 'print 1;'
# print(s)
# print(parse_source(s))
# print()

# print('prelim 2')
# s = 'print 2.5;'
# print(s)
# print(parse_source(s))
# print()

# print('prelim 3a')
# s = '1 + 2;'
# print(s)
# print(parse_source(s))
# print()

# print('prelim 3')
# s = 'print 4 * 2 + 3 * 4 / 701 - 1;'
# print(s)
# print(parse_source(s))
# print()

# print('prelim 4')
# s = 'var x = 3;'
# print(s)
# print(parse_source(s))
# print()

# print('prelim 5')
# s = 'print 2 + x;'
# print(s)
# print(parse_source(s))
# print()

# print(0)
# s = "2 + 3 * 4;"
# print(s)
# print(parse_source(s))
# print()

# print(1)
# s = """
    # print 2 + 3 * -4;
    # print 2.0 - 3.0 / -4.0;
    # print -2 + 3;
    # print 2 * 3 + -4;
# """
# print(s)
# print(parse_source(s))
# print()

# print(2)
# s = """
    # const pi = 3.14159;
    # var tau float;
    # tau = 2.0 * pi;
    # print tau;
# """
# print(s)
# print(parse_source(s))
# print()

# print(3)
# s = '''
    # var a int = 2;
    # var b int = 3;
    # if a < b {
        # print a;
    # } else {
        # print b;
    # }
# '''
# print(s)
# print(parse_source(s))
# print()

# print(4)
# s = '''
    # const n = 10;
    # var x int = 1;
    # var fact int = 1;

    # while x < n {
        # fact = fact * x;
        # print fact;
        # x = x + 1;
    # }
# '''
# print(s)
# print(parse_source(s))
# print()

# print(5)
# s = '''
    # var x = 37;
    # var y = 42;
    # x = { var t = y; y = x; t; };     // Compound expression.
    # print x;
    # print y;
# '''
# print(s)
# print(parse_source(s))
# print()

print(6, 0)
s = '''
func add(x int, y int) int {
    return x + y;
}
'''
s = '''
func add(x int, y int) int {
  woo;
}
'''
print(s)
print(parse_source(s))
print()

print(6, 1)
s = '''
func add(x int, y int) int {
    return x + y;
}
'''
s = '''
func add(x int, y int) int {
  return x + y;
}
'''
print(s)
print(parse_source(s))
print()

print(6, 2)
s = '''
add(x, y);
'''
print(s)
print(parse_source(s))
print()

print(6, 3)
s = '''
add(x, y);
'''
print(s)
print(parse_source(s))
print()

print(6, 'full')
s = '''
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
print(s)
print(parse_source(s))
print()

