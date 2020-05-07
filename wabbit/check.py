# typecheck.py
#
# Type Checking
# =============
# This file implements type checking. Wabbit uses what's known as
# "nomimal typing."  That means that types are given unique
# names such as "int", "float", "bool", etc. Two types are the same
# if they have exactly the same name.  That's it.
#
# In implementing the type checker, the best strategy might be to
# not overthink the problem at hand. Basically, you have type names.
# You can represent these names using Python strings and compare them
# using string comparison. This gives you most of what you need.
#
# In some cases, you might need to check combinations of types against a
# large number of cases (such as when implementing the math operators).
# For that, it helps to make lookup tables.  For example, you can use
# Python dictionaries to build lookup tables that encode valid
# combinations of binary operators.  For example:
#
# _binops = {
#     # ('lefttype', 'op', 'righttype') : 'resulttype'
#     ('int', '+', 'int') : 'int',
#     ('int', '-', 'int') : 'int',
#     ...
# }
#
# The directory tests/Errors has Wabbit programs with various errors.

from .model import *


def check_statements(statements):
    return check_program(Program(statements))


def check_program(program):
    # Make the initial environment (a dict)
    ctx = {}
    checker = Checker()
    program.visit(checker, ctx)
    return checker.errors


class Checker(ScopeAwareModelVisitor):
    '''
    This checker is implemented as a ScopeAwareModelVisitor which evaluates wabbit, verifying it, and propagates
    return type of each node to assist.
    '''
    def __init__(self):
        self.env = ChainMap()
        self.errors = []

    def log_error(self, error):
        self.errors.append(error)
    
    def visit_StorageIdentifier(self, node, ctx):
        # gimme the key for this name in this context
        return str(node.name)
    
    def visit_StorageLocation(self, node, ctx):
        # gimme the type for the key in this context
        name = node.identifier.visit(self, ctx)
        storage = self.getStash(ctx, name)
        return storage._type
    
    def visit_DeclStorageLocation(self, node, ctx):
        # I'll store values in this name in this context with this key and this type
        return None
        raise NotImplementedError

    def visit_FuncCall(self, node, ctx):
        return None
        raise NotImplementedError

    def visit_FuncDeclStatement(self, node, ctx):
        return None
        raise NotImplementedError
    
    def visit_AssignStatement(self, node, ctx):
        # Store a value in the locaiton with this name
        name = node.location.visit(self, ctx)
        if not self.chkStash(ctx, name):
            self.log_error("Can't assign to undeclared location")
            return None

        storage = self.getStash(ctx, name)
        if storage.is_const():
            self.log_error("Can't assign to a constant variable")

        value_type = node.value.visit(self, ctx)
        if storage._type != value_type:
            self.log_error("Type mismatch error")
        return None
    
    def visit_PrintStatement(self, node, ctx):
        return None
    
    def visit_ConditionalStatement(self, node, ctx):
        return None
    
    def visit_ConditionalLoopStatement(self, node, ctx):
        return None
    
    def visit_ContinueLoopStatement(self, node, ctx):
        return None
    
    def visit_BreakLoopStatement(self, node, ctx):
        return None
    
    def visit_ExpressionStatement(self, node, ctx):
        return node.statement.visit(self, ctx)
    
    def visit_ReturnStatement(self, node, ctx):
        return True
        raise NotImplementedError
    
    def visit_BinOp(self, node, ctx):
        return True
        raise NotImplementedError
    
    def visit_UnOp(self, node, ctx):
        return True
        raise NotImplementedError
    
    def visit_BlockExpression(self, node, ctx):
        ret = None
        ctx = self.newScope(ctx)
        for stmt in node.block.statements:
            ret = stmt.visit(self, ctx)
        return ret
    
    def visit_Int(self, node, ctx):
        return 'int'
    
    def visit_Char(self, node, ctx):
        return 'char'
    
    def visit_Float(self, node, ctx):
        return 'float'
