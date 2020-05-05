#!/usr/bin/env python3

# type_models.py
#
# The WabbitType language extends WabbitScript with support for
# user-defined types including structures and enums. This is, by
# far, the most difficult part of the project. Please see
# the following:
#
# https://github.com/dabeaz/compilers_2020_05/wiki/WabbitType.md
#
# DO NOT WORK ON THIS UNLESS YOU HAVE EVERYTHING ELSE WORKING!
#

from wabbit.model import *
from wabbit.source_visitor import compare_source

# -----------------------------------------------------------------------------
# Program 7: Structures.  The following program defines and uses a structure.
#
# You'll need to support structure definition, creation, and usage with other
# parts of your language such as functions.

source7 = '''
struct Fraction {
    numerator int;
    denominator int;
}

func frac_mul(a Fraction, b Fraction) Fraction {
    return Fraction(a.numerator * b.numerator, a.denominator * b.denominator);
}

var x = Fraction(1, 4);
var y = Fraction(3, 8);
var c = frac_mul(x, y);
print c.numerator;
print c.denominator;
c.numerator = c.numerator / 4;
c.denominator = c.denominator / 4;
print c.numerator;
print c.denominator;
'''

model7 = Block([
    Struct(Name('Fraction'), [
        Arg(Name('numerator'), 'int'),
        Arg(Name('denominator'), 'int'),
    ]),
    Func(Name('frac_mul'),
        Block([
            Return(
                Call(Name('Fraction'), [
                    BinOp('*', Name('a.numerator'), Name('b.numerator')),
                    BinOp('*', Name('a.denominator'), Name('b.denominator')),
                ]),
            ),
        ], indent=' '*4),
        [Arg(Name('a'), 'Fraction'), Arg(Name('b'), 'Fraction')],
        ret_type='Fraction',
    ),
    Var(Name('x'), Call(Name('Fraction'), [Integer(1), Integer(4)])),
    Var(Name('y'), Call(Name('Fraction'), [Integer(3), Integer(8)])),
    Var(Name('c'), Call(Name('frac_mul'), [Name('x'), Name('y')])),
    Print(Name('c.numerator')),
    Print(Name('c.denominator')),
    Assign(Name('c.numerator'), BinOp('/', Name('c.numerator'), Integer(4))),
    Assign(Name('c.denominator'), BinOp('/', Name('c.denominator'), Integer(4))),
    Print(Name('c.numerator')),
    Print(Name('c.denominator')),
])

compare_source(model7, source7)

# -----------------------------------------------------------------------------
# Program 8: Enums.  The following program defines and uses an enum.
#
# To this, you'll need to support the enum definition, enum values,
# and various forms of pattern matching including match, if let, and
# while let.

source8 = '''
enum MaybeNumber {
    No;
    Integer(int);
    Float(float);
}

func add(a Number, b Number) Number {
   return match(a) {
             No => Number::No;
             Integer(x) => match(b) {
                   Integer(y) => Number::Integer(x + y);
                   Float(y) => Number::Float(float(x) + y);
             };
             Float(x) => match(b) {
                   Integer(y) => Number::Float(x + float(x));
                   Float(y) => Number::Float(x + y);
             };
   };
}

var a = Number::Integer(42);
var b = Number::Float(3.7);
var c = add(a, b);

if let Float(x) = c {
    print x;
} else {
    print 0.0;
}

while let Integer(x) = a {
    print x;
    if x > 0 {
        a = Number::Integer(x-1);
    } else {
        a = Number::No;
    }
}
'''

model8 = Block([])

compare_source(model8, source8)
