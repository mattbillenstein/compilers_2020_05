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
class Node:
    """
    Top-level class for all model elements/nodes
    """

    pass


class Statement(Node):
    pass


class Expression(Node):
    pass


class Definition(Node):
    """
    A definition of some kind e.g. var/const
    """

    pass


class Location(Node):
    """
    A place to put something
    """

    pass


class Argument(Definition):
    """
    Example func mul(x int) {
    """

    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __repr__(self):
        return f"Argument({self.name}, {self.type})"

    def to_source(self):
        return f"{self.name} {self.type}"


class Arguments(Expression):
    """
    Example func mul(x int, y int) {
    """

    def __init__(self, args):
        self.args = args

    def __repr__(self):
        return f"Arguments({self.args})"

    def to_source(self):
        return ", ".join([s.to_source() for s in self.args])


class FunctionCall(Expression):
    """
    Example mul(n, 5)
    """

    def __init__(self, name, *args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"FunctionCall({self.name}, {self.args})"

    def to_source(self):
        args = ", ".join([s.to_source() for s in self.args])
        return f"{self.name}({args})"


class FunctionDefinition(Definition):
    """
    Example func mul(x int, y int) int {
    }
    """

    def __init__(self, name, args=None, return_type=None, body=None):
        self.name = name
        self.args = args
        self.return_type = return_type
        self.body = body

    def __repr__(self):
        return f"FunctionDefinition({self.name}, {self.args}, {self.return_type}, {self.body})"

    def to_source(self):
        if self.return_type:
            return_type = self.return_type.to_source()
        else:
            return_type = f""
        if self.body:
            body = self.body.to_source()
        else:
            body = f""
        if self.args:
            args = self.args.to_source()

        else:
            args = f""
        return f"func {self.name}({args}) {return_type} {{ \n {body}\n}}"


class Block(Expression):
    """
    Example x = { var t = y; y = x; t; }; // Compound expression.
    """

    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Block({self.statements})"

    def to_source(self):
        joined_statements = "; ".join([s.to_source() for s in self.statements])
        return f"{{ {joined_statements} }}"


class Statements(Statement):
    """
    Example:
    var a int;
    a = 3
    """

    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Statements({self.statements})"

    def to_source(self):
        return "\n".join([s.to_source() for s in self.statements])


class If(Statement):
    """
    Example if x < y
    """

    def __init__(self, test, when_true, when_false):
        assert isinstance(test, Expression)
        assert isinstance(when_true, Statement)
        assert isinstance(when_false, Statement)
        self.test = test
        self.when_true = when_true
        self.when_false = when_false

    def __repr__(self):
        return f"If({self.test}, {self.when_true}, {self.when_false})"

    def to_source(self):
        return f"if {self.test.to_source()} {{\n   {self.when_true.to_source()}\n}} else {{\n   {self.when_false.to_source()}\n}}"


class While(Statement):
    """
    Example while x < y
    """

    def __init__(self, test, when_true):
        assert isinstance(test, Expression)
        assert isinstance(when_true, Statement)
        self.test = test
        self.when_true = when_true

    def __repr__(self):
        return f"While({self.test}, {self.when_true})"

    def to_source(self):
        return f"while {self.test.to_source()} {{\n   {self.when_true.to_source()}\n}}"


class Assignment(Statement):
    """
    Example: foo = 7
    """

    def __init__(self, location, expression):
        self.location = location
        self.expression = expression

    def __repr__(self):
        return f"Assignment({self.location}, {self.expression})"

    def to_source(self):
        return f"{self.location.to_source()} = {self.expression.to_source()}"


class Print(Statement):
    """
    Example: print 3
    """

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Print({self.value})"

    def to_source(self):
        return f"print {self.value.to_source()}"


class Return(Statement):
    """
    Example: return 3
    """

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Return({self.value})"

    def to_source(self):
        return f"return {self.value.to_source()}"


class Float(Expression):
    """
    Example: 3.14
    """

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Float({self.value})"

    def to_source(self):
        return repr(self.value)


class Const(Definition):
    """
    Example: const bar
    """

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Const({self.value})"

    def to_source(self):
        return f"const {self.value}"


class Var(Definition):
    """
    Example: var foo
    """

    def __init__(self, value, type=None):
        self.value = value
        self.type = type

    def __repr__(self):
        if self.type:
            return f"Var({self.value}, {self.type})"
        return f"Var({self.value})"

    def to_source(self):
        if self.type:
            return f"var {self.value} {self.type}"
        return f"var {self.value}"


class Variable(Location):
    """
    Example: pi
    """

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Variable({self.value})"

    def to_source(self):
        return self.value


class Integer(Expression):
    """
    Example: 42
    """

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Integer({self.value})"

    def to_source(self):
        return repr(self.value)


class UnaryOp(Expression):
    """
    Example: -32
    """

    def __init__(self, op, target):
        self.op = op
        self.target = target

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.target})"

    def to_source(self):
        return f"{self.op}{self.target.to_source()}"


class BinOp(Expression):
    """
    Example: left + right
    """

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinOp({self.op}, {self.left}, {self.right})"

    def to_source(self):
        return f"{self.left.to_source()} {self.op} {self.right.to_source()}"


# ------ Debugging function to convert a model into source code (for easier viewing)


def to_source(node):
    try:
        print(node.to_source())
    except:
        raise RuntimeError(f"Can't convert {node} to source")

