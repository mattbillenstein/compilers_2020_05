from wabbit.c import ccompile, compile_program
from wabbit.model import *
from wabbit.parse import parse_source

def ctc(s):
    env = {}
    node = parse_source(s)
    return ccompile(node, env)

def test_add():
    out = ctc('1+1;')
    expected = '''_I2 = 1;
_I3 = 1;
_BinOp1 = _I3 + _I2;'''
    assert out == expected

def test_var():
    s = '''var x int = 1;
var y int = x + 2;
print x;
print y;
'''
    out = ctc(s)
    print(out)
    expected = '''_I1 = 1;
x = _I1;
_I3 = 2;
_BinOp1 = x + _I3;
y = _BinOp1;
printf("%i\\n", x);
printf("%i\\n", y);'''
    assert out == expected

def test_precedence():
    out = ctc('3 + 1 * 2 - 7 * -4;')
    print(out)
    expected = '''_I5 = 4;
_UnaryOp1 = -_I5;
_I6 = 7;
_BinOp4 = _I6 * _UnaryOp1;
_I7 = 2;
_I8 = 1;
_BinOp5 = _I8 * _I7;
_I9 = 3;
_BinOp6 = _I9 + _BinOp5;
_BinOp7 = _BinOp6 - _BinOp4;'''
    assert out == expected
