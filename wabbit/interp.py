# interp.py
#
# In order to write a compiler for a programming language, it helps to
# have some kind of specification of how programs written in the
# programming language are actually supposed to work. A language is
# more than just "syntax" or a data model.  There has to be some kind
# of operational semantics that describe what happens when a program
# runs.
#
# One way to specify the operational semantics is to write a so-called
# "definitional interpreter" that directly executes the data
# model. This might seem like cheating--after all, our final goal is
# not to write an interpreter, but a compiler. However, if you can't
# write an interpreter, chances are you can't write a compiler either.
# So, the purpose of doing this is to pin down fine details as well as
# our overall understanding of what needs to happen when programs run.
#
# We'll write our interpreter in Python.  The idea is relatively 
# straightforward.  For each class in the model.py file, you're
# going to write a function similar to this:
#
#    def interpret_node_name(node, env):
#        # Execute "node" in the environment "env"
#        ...
#        return result
#   
# The input to the function will be an object from model.py (node)
# along with an object respresenting the execution environment (env).
# The function will then execute the node in the environment and return
# a result.  It might also modify the environment (for example,
# when executing assignment statements, variable definitions, etc.). 
#
# For the purposes of this projrect, assume that all programs provided
# as input are "sound"--meaning that there are no programming errors
# in the input.  Our purpose is not to create a "production grade"
# interpreter.  We're just trying to understand how things actually
# work when a program runs. 
#
# For testing, try running your interpreter on the models you
# created in the example_models.py file.
#

from .model import *

# Top level function that interprets an entire program. It creates the
# initial environment that's used for storing variables.


def interpret_program(model):
    # Make the initial environment (a dict)
    env = {}
    interpreter = Interpreter(env)
    interpreter.run(model)


class Storage():
    def __init__(self, _type, const):
        self._type = _type
        self.const = const


class Interpreter(ModelVisitor):
    def __init__(self, env):
        self.env = env

    def visit_Location(self, node):
        return self.env[node.identifier]

    def visit_DeclLocation(self, node):
        if node.identifier in self.env.keys():
            raise
        self.env[node.identifier] = Storage(node._type, node.const)
        return self.visit_Location(node)

    def visit_ScalarNode(self, node):
        return node.value

    def visit_AssignStatement(self, node):
        storage = node.location.visit(self)
        storage.assign(node.value)
        return node.value

    def visit_BinOp(self, node):
        lhs = node.left.visit(self)
        rhs = node.right.visit(self)
        if node.op == '>':
            return lhs > rhs
        elif node.op == '<':
            return lhs < rhs
        elif node.op == '==':
            return lhs == rhs
        elif node.op == '!=':
            return lhs != rhs
        elif node.op == '<=':
            return lhs <= rhs
        elif node.op == '>=':
            return lhs >= rhs
        elif node.op == '||':
            return lhs or rhs  # XXX short-circuit
        elif node.op == '&&':
            return lhs and rhs  # XXX short-circuit
        elif node.op == '+':
            return lhs + rhs
        elif node.op == '/':
            return lhs / rhs
        elif node.op == '*':
            return lhs * rhs
        elif node.op == '-':
            return lhs - rhs
        else:
            raise

    def visit_UnOp(self, node):
        rhs = node.right.visit(self)
        if node.op == '!':
            return not rhs
        elif node.op == '+':
            return rhs
        elif node.op == '-':
            return rhs * -1
        else:
            raise

    def visit_PrintStatement(self, node):
        print(node.expr.visit(self))
        return None

    def visit_ConditionalStatement(self, node):
        block = None
        if node.cond.visit(self):
            block = self.blockT
        else:
            block = self.blockF
        for stmt in block:
            stmt.visit(self)
        return None

    def visit_ConditionalLoopStatement(self, node):
        while node.cond.visit(self):
            for stmt in node.block:
                stmt.visit(self)
        return None

    def visit_BlockExpression(self, node):
        ret = None
        for stmt in node.block:
            ret = stmt.visit(self)
        return ret

    def visit_ExpressionStatement(self, node):
        return node.statement.visit(self)

    def visit_FuncCall(self, node):
        pass  # XXX

    def visit_FuncDeclStatement(self, node):
        pass  # XXX

    def visit_ReturnStatement(self, node):
        pass  # XXX
