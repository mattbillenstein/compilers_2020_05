from wabbit.tokenize import *

def go(s):
    print(s)
    for each in tokenize(s):
        print(each)

go('123')
print()

print(0)
go("2 + 3 * 4;")
print()

print(1)
source1 = """
    print 2 + 3 * -4;
    print 2.0 - 3.0 / -4.0;
    print -2 + 3;
    print 2 * 3 + -4;
"""
go(source1)
print()

print(2)
source2 = """
    const pi = 3.14159;
    var tau float;
    tau = 2.0 * pi;
    print tau;
"""
go(source2)
print()

print(3)
source3 = '''
    var a int = 2;
    var b int = 3;
    if a < b {
        print a;
    } else {
        print b;
    }
'''
go(source3)
print()

print(4)
source4 = '''
    const n = 10;
    var x int = 1;
    var fact int = 1;

    while x < n {
        fact = fact * x;
        print fact;
        x = x + 1;
    }
'''
go(source4)
print()
