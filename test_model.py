
# Monday after lunch: Dave says try to make the data structure of your program enforce correctness as much as possible.
# he gives the example that certain types of things should only work with other types of things (and could error otherwise)

# what does this mean? what is correct?
# so far node-wise we have

# so an expression is something you can evaluate
# a statement is part of the language (if, print)

# class Integer: # should be passed an int
    # # when evaluated returns an int
# class Float: # should be passed a float
    # # when evaluated returns a float
# class BinOp: # should have one of our allowed binops then 2 things that comes down to a variable
    # # when evaluated could be a int, float
# class PrintStatement: # ??? can have parens and can not, can't take a str, only a char... eep
    # # cannot be evaluated
# class Const: # Declaration of a const, It's like a var, but it can't be assigned to outside of initialization
# class Var: # Declaration of a var
# class Assign: # puts the rhs into the lhs, lhs must be assignable, rhs must come down to a... thing.
# class Variable: # a thing you can put stuff in, or a way to get to one
# class Compare: # is this a binop
# class If: # it's gotta have a thing that comes down to a bool.. but we don't have types, it's gotta have an expression then?
# class IfElse: #
# class While: #
# class CompoundExpression: # a bunch of statements that return the evaluation of the last statement

# which ones end with ';'?
# which ones can be the lhs of assignment?
# let's put the to_source on the classes
# which ones can be top level statements?

from wabbit.model import *

x = Integer('a')
assert(not x.is_correct())
x = Integer(1)
assert(x.is_correct())

x = BinOp(1, 2, 3)
assert(not x.is_correct())
x = BinOp('<', Integer(2), Integer(3))
assert(x.is_correct())
