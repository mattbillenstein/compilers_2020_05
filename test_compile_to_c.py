from wabbit.c import ccompile, compile_program, compile_statements_as_string
from wabbit.model import *
from wabbit.parse import parse_source

def ctc(s):
    node = parse_source(s)
    return compile_statements_as_string(node)

def test_add():
    out = ctc('1+1;')
    print(out)
    expected = '''int _I0;
int _I1;
int _BinOp0;
_I0 = 1;
_I1 = 1;
_BinOp0 = _I1 + _I0;'''
    assert out == expected

def test_var():
    s = '''var x int = 1;
var y int = x + 2;
print x;
print y;
'''
    out = ctc(s)
    print(out)
    expected = '''int _I0;
int x;
int _I1;
int _BinOp0;
int y;
_I0 = 1;
x = _I0;
_I1 = 2;
_BinOp0 = x + _I1;
y = _BinOp0;
printf("%i\\n", x);
printf("%i\\n", y);'''
    assert out == expected

def test_precedence():
    out = ctc('3 + 1 * 2 - 7 * -4;')
    print(out)
    expected = '''int _I0;
int _UnaryOp0;
int _I1;
int _BinOp0;
int _I2;
int _I3;
int _BinOp1;
int _I4;
int _BinOp2;
int _BinOp3;
_I0 = 4;
_UnaryOp0 = -_I0;
_I1 = 7;
_BinOp0 = _I1 * _UnaryOp0;
_I2 = 2;
_I3 = 1;
_BinOp1 = _I3 * _I2;
_I4 = 3;
_BinOp2 = _I4 + _BinOp1;
_BinOp3 = _BinOp2 - _BinOp0;'''
    assert out == expected
