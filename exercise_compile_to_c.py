from wabbit.c import ccompile, compile_program
from wabbit.model import *
from wabbit.parse import parse_source

def harness(name, source):
    print(name)
    print('source:', source)
    env = {}
    node = parse_source(source)
    print('model: ', node)
    print('ccompiled:', ccompile(node, env))
    print('env after:', env)
    print('compiled_program:', compile_program(node))
    print()

harness('0', '1+1;')

harness('0.1', '1.0+1.0;')

# with vars we've got to do everything and then go back and add the vars at the top.
# should compile away to nothing
harness('1.0', 'var x;')

# should be
# int x;
# x = 10;
harness('1.1', '''
var x;
x = 10;
''')

harness('1.2', '''
var x int;
x = 20;
''')

harness('1.2', '''
const x = 703;
''')

harness('2.0', '''
print 1;
''')

harness('3.0', '''
var x int = 0;
while x < 10 {
    print x;
}
''')


# TODO while
