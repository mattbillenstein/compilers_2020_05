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

# -----------------------------------------------------------------------------
# Program 7: Structures.  The following program defines and uses a structure.
#
# You'll need to support structure definition, creation, and usage with other
# parts of your language such as functions.

source7 = """
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
"""

model7 = Statements(
    [
        Struct(
            "Fraction", Argument("numerator", "int"), Argument("denominator", "int")
        ),
        FunctionDefinition(
            "frac_mul",
            Arguments(Argument("a", "Fraction"), Argument("b", "Fraction")),
            Variable("Fraction"),
            Return(
                FunctionCall(
                    "Fraction",
                    BinOp("*", Variable("a.numerator"), Variable("b.numerator")),
                    BinOp("*", Variable("a.denominator"), Variable("b.denominator")),
                )
            ),
        ),
        Assignment(Var("x"), FunctionCall("Fraction", Integer(1), Integer(4))),
        Assignment(Var("y"), FunctionCall("Fraction", Integer(3), Integer(8))),
        Assignment(Var("c"), FunctionCall("frac_mul", Variable("x"), Variable("y"))),
        Print(Variable("c.numerator")),
        Print(Variable("c.denominator")),
        Assignment(
            Variable("c.numerator"), BinOp("/", Variable("c.numerator"), Integer(4))
        ),
        Assignment(
            Variable("c.denominator"), BinOp("/", Variable("c.denominator"), Integer(4))
        ),
        Print(Variable("c.numerator")),
        Print(Variable("c.denominator")),
    ]
)

print(to_source(model7))

# -----------------------------------------------------------------------------
# Program 8: Enums.  The following program defines and uses an enum.
#
# To this, you'll need to support the enum definition, enum values,
# and various forms of pattern matching including match, if let, and
# while let.

source8 = """
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
"""

model8 = Statements(
    [
        Enum(
            "MaybeNumber",
            EnumChoice("No"),
            EnumChoice("Integer", "int"),
            EnumChoice("Float", "float"),
        ),
        FunctionDefinition(
            "add",
            Arguments(Argument("a", "Number"), Argument("b", "Number")),
            Variable("Number"),
            Return(
                Match(
                    "a",
                    MatchCondition(EnumChoice("No"), EnumChoice("Number::No")),
                    MatchCondition(
                        EnumChoice("Integer", "x"),
                        Match(
                            "b",
                            MatchCondition(
                                EnumChoice("Integer", "y"),
                                EnumLocation(
                                    "Number",
                                    "Integer",
                                    Arguments(BinOp("+", Variable("x"), Variable("y"))),
                                ),
                            ),
                            MatchCondition(
                                EnumChoice("Float", "y"),
                                EnumLocation(
                                    "Number",
                                    "Float",
                                    Arguments(
                                        BinOp(
                                            "+",
                                            FunctionCall("float", Variable("x")),
                                            Variable("y"),
                                        ),
                                        Variable("y"),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    MatchCondition(
                        EnumChoice("Float", "x"),
                        Match(
                            "b",
                            MatchCondition(
                                EnumChoice("Integer", "y"),
                                EnumLocation(
                                    "Number",
                                    "Float",
                                    Arguments(
                                        BinOp(
                                            "+",
                                            Variable("x"),
                                            FunctionCall("float", Variable("x")),
                                        )
                                    ),
                                ),
                            ),
                            MatchCondition(
                                EnumChoice("Float", "y"),
                                EnumLocation(
                                    "Number",
                                    "Float",
                                    Arguments(BinOp("+", Variable("x"), Variable("y"))),
                                ),
                            ),
                        ),
                    ),
                )
            ),
        ),
    ]
)
print(to_source(model8))
