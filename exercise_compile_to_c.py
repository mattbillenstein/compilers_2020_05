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

# harness('0.1', '1.0+1.0;')

# # with vars we've got to do everything and then go back and add the vars at the top.
# # should compile away to nothing
# harness('1.0', 'var x;')

# # should be
# # int x;
# # x = 10;
# harness('1.1', '''
# var x;
# x = 10;
# ''')

# harness('1.2', '''
# var x int;
# x = 20;
# ''')

# harness('1.2', '''
# const x = 703;
# ''')

# harness('2.0', '''
# print 1;
# ''')

# harness('3.0', '''
# var x int = 0;
# while x < 10 {
    # print x;
# }
# ''')

# harness('fib', '''
# var a int = 1;
# var b int = 1;
# var t int;
# var n int = 0;
# const LAST = 20;
# while n < LAST {
    # print a;
    # t = a + b;
    # a = b;
    # b = t;
    # n = n + 1;
# }
# ''')

# harness('fact', '''
# var n int = 1;
# var value int = 1;
# while n < 10 {
    # value = value * n;
    # print value ;
    # n = n + 1;
# }
# ''')

# harness('nested whiles', '''
# while blah {
  # while blurgh {
    # while splurgh {
    # }
  # }
# }
# ''')

# harness('many vars', '''
# var x int = 0;
# x = x + 1;
# ''')

harness('mandel_loop', '''
const xmin = -2.0;
const xmax = 1.0;
const ymin = -1.5;
const ymax = 1.5;
const width = 80.0;
const height = 40.0;
const threshhold = 1000;

var dx float = (xmax - xmin)/width;
var dy float = (ymax - ymin)/height;
var y float = ymax;
var x float;
var _x float;
var _y float;
var xtemp float;
var n int;
var in_mandel bool;
while y >= ymin {
     x = xmin;
     while x < xmax {
         _x = 0.0;
         _y = 0.0;
         n = threshhold;
         in_mandel = true;
         while n > 0 {
             xtemp = _x*_x - _y*_y + x;
             _y = 2.0*_x*_y + y;
             _x = xtemp;
             n = n - 1;
             if (_x*_x + _y*_y) > 4.0 {
                 in_mandel = false;
                 n = 0;
             }
         }
         if in_mandel {
             print '*';
         } else {
             print '.';
         }
         x = x + dx;
     }
     print '\\n';
     y = y - dy;
}
''')
