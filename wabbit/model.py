# model.py
#
# This file defines the data model for Wabbit programs.  The data
# model is a data structure that represents the contents of a program
# as objects, not text.  Sometimes this structure is known as an
# "abstract syntax tree" or AST.  However, the model is not
# necessarily directly tied to the actual syntax of the language.  So,
# we'll prefer to think of it as a more generic data model instead.
#
# To do this, you need to identify the different "elements" that make
# up a program and encode them into classes.  To do this, it may be
# useful to slightly "underthink" the problem. To illustrate, suppose
# you wanted to encode the idea of "assigning a value."  Assignment
# involves a location (the left hand side) and a value like this:
#
#         location = expression;
#
# To represent this idea, make a class with just those parts:
#
#     class Assignment:
#         def __init__(self, location, expression):
#             self.location = location
#             self.expression = expression
#
# What are "location" and "expression"?  Does it matter? Maybe
# not. All you know is that an assignment operator definitely requires
# both of those parts.  DON'T OVERTHINK IT.  Further details will be
# filled in as the project evolves.
#
# Work on this file in conjunction with the top-level
# "script_models.py" file.  Go look at that file and see what program
# samples are provided.  Then, figure out what those programs look like
# in terms of data structures.
#
# There is no "right" solution to this part of the project other than
# the fact that a program has to be represented as some kind of data
# structure that's not "text."   You could use classes. You could use
# tuples. You could make a bunch of nested dictionaries like JSON.
# The key point: it must be a data structure.
#
# Starting out, I'd advise against making this file too fancy. Just
# use basic data structures. You can add usability enhancements later.
# -----------------------------------------------------------------------------

# The following classes are used for the expression example in script_models.py.
# Feel free to modify as appropriate.  You don't even have to use classes
# if you want to go in a different direction with it.


class If:
    """
    Example if x < y
    """

    def __init__(self, test, when_true, when_false):
        self.test = test
        self.when_true = when_true
        self.when_false = when_false

    def __repr__(self):
        return f"If({self.test}, {self.when_true}, {self.when_false})"


class Assignment:
    """
    Example: foo = 7
    """

    def __init__(self, location, expression):
        self.location = location
        self.expression = expression

    def __repr__(self):
        return f"Assignment({self.location}, {self.expression})"


class Print:
    """
    Example: print 3
    """

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Print({self.value})"


class Float:
    """
    Example: 3.14
    """

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Float({self.value})"


class Const:
    """
    Example: const bar
    """

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Const({self.value})"


class Var:
    """
    Example: var foo
    """

    def __init__(self, value, type):
        self.value = value
        self.type = type

    def __repr__(self):
        return f"Var({self.value}, {self.type})"


class Variable:
    """
    Example: pi
    """

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Variable({self.value})"


class Integer:
    """
    Example: 42
    """

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Integer({self.value})"


class UnaryOp:
    """
    Example: -32
    """

    def __init__(self, op, target):
        self.op = op
        self.target = target

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.target})"


class BinOp:
    """
    Example: left + right
    """

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinOp({self.op}, {self.left}, {self.right})"


# ------ Debugging function to convert a model into source code (for easier viewing)


def to_source(node):
    if isinstance(node, list):
        return "\n".join([to_source(item) for item in node])
    elif isinstance(node, Integer):
        return repr(node.value)
    elif isinstance(node, Const):
        return f"const {node.value}"
    elif isinstance(node, Variable):
        return node.value
    elif isinstance(node, Var):
        return f"var {node.value} {node.type}"
    elif isinstance(node, Assignment):
        return f"{to_source(node.location)} = {to_source(node.expression)}"
    elif isinstance(node, Float):
        return repr(node.value)
    elif isinstance(node, Print):
        return f"print {to_source(node.value)}"
    elif isinstance(node, If):
        return f"if {to_source(node.test)} {{\n   {to_source(node.when_true)}\n}} else {{\n   {to_source(node.when_false)}\n}}"
    elif isinstance(node, UnaryOp):
        return f"{node.op}{to_source(node.target)}"
    elif isinstance(node, BinOp):
        return f"{to_source(node.left)} {node.op} {to_source(node.right)}"
    else:
        raise RuntimeError(f"Can't convert {node} to source")

