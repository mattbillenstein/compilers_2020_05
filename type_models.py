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

from wabbit.interp import interpret
from wabbit.model import *
from wabbit.parse import parse
from wabbit.source import compare_source

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

struct Foo {
    frac Fraction;
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
var d = Foo(Fraction(7, 8));
print d.frac.numerator;
print d.frac.denominator;
d.frac.numerator = 1;
d.frac.denominator = 2;
print d.frac.numerator;
print d.frac.denominator;
'''

model7 = Block([
    Struct(Name('Fraction'), [
        Field(Name('numerator'), Type('int')),
        Field(Name('denominator'), Type('int')),
    ]),
    Struct(Name('Foo'), [
        Field(Name('frac'), Type('Fraction')),
    ]),
    Func(Name('frac_mul'),
        Block([
            Return(
                Call(Name('Fraction'), [
                    BinOp('*', Attribute(Name('a'), 'numerator'), Attribute(Name('b'), 'numerator')),
                    BinOp('*', Attribute(Name('a'), 'denominator'), Attribute(Name('b'), 'denominator')),
                ]),
            ),
        ], indent=' '*4),
        [ArgDef(Name('a'), Type('Fraction')), ArgDef(Name('b'), Type('Fraction'))],
        ret_type=Type('Fraction'),
    ),
    Var(Name('x'), Call(Name('Fraction'), [Integer(1), Integer(4)])),
    Var(Name('y'), Call(Name('Fraction'), [Integer(3), Integer(8)])),
    Var(Name('c'), Call(Name('frac_mul'), [Name('x'), Name('y')])),
    Print(Attribute(Name('c'), 'numerator')),
    Print(Attribute(Name('c'), 'denominator')),
    Assign(Attribute(Name('c'), 'numerator'), BinOp('/', Attribute(Name('c'), 'numerator'), Integer(4))),
    Assign(Attribute(Name('c'), 'denominator'), BinOp('/', Attribute(Name('c'), 'denominator'), Integer(4))),
    Print(Attribute(Name('c'), 'numerator')),
    Print(Attribute(Name('c'), 'denominator')),

    # nested structs...
    Var(Name('d'), Call(Name('Foo'), [Call(Name('Fraction'), [Integer(7), Integer(8)])])),
    Print(Attribute(Attribute(Name('d'), 'frac'), 'numerator')),
    Print(Attribute(Attribute(Name('d'), 'frac'), 'denominator')),
    Assign(Attribute(Attribute(Name('d'), 'frac'), 'numerator'), Integer(1)),
    Assign(Attribute(Attribute(Name('d'), 'frac'), 'denominator'), Integer(2)),
    Print(Attribute(Attribute(Name('d'), 'frac'), 'numerator')),
    Print(Attribute(Attribute(Name('d'), 'frac'), 'denominator')),
])

compare_source(model7, source7)
x, env, stdout = interpret(model7)
assert stdout == [3, 32, 0, 8, 7, 8, 1, 2], (x, env, stdout)
compare_model(parse(source7), model7)

# -----------------------------------------------------------------------------
# Program 8: Enums.  The following program defines and uses an enum.
#
# To this, you'll need to support the enum definition, enum values,
# and various forms of pattern matching including match, if let, and
# while let.

source8 = '''
enum Number {
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

model8 = Block([
    Enum(Name('Number'), [
        Member(Name('No')),
        Member(Name('Integer'), Type('int')),
        Member(Name('Float'), Type('float')),
    ]),
    Func(Name('add'),
        Block([
#            Return(
#                Match(Name('a'), [
#                ]),
#            ),
        ]),
        [ArgDef(Name('a'), Type('Number')), ArgDef(Name('b'), Type('Number'))],
        ret_type=Type('Number'),
    ),
])

#compare_source(model8, source8)
#x, env, stdout = interpret(model8)
#assert stdout == [1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880], (x, env, stdout)
