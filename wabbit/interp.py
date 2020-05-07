from .model import *
from collections import ChainMap


def interpret_program(program):
    # Make the initial environment (a dict)
    stdout = []
    global_ctx = {}
    interpreter = Interpreter(stdout)
    program.visit(interpreter, global_ctx)
    return stdout


def interpret_statements(statements):
    return interpret_program(Program(statements))


UNDEF = object()


class Storage():
    def __init__(self, _type, const):
        self._type = _type
        self.const = const
        self.value = UNDEF

    def is_unset(self):
        return self.value == UNDEF

    def set(self, value):
        self.value = value
        return None

    def get(self):
        if self.value is UNDEF:
            raise RuntimeError()
        return self.value


class Interpreter(ScopeAwareModelVisitor):
    '''
    This interpreter is implemented as a ScopeAwareModelVisitor which evaluates wabbit, executing it, and propagates
    return values of each node to assist.
    '''
    def __init__(self, stdout):
        self.stdout = stdout

    def visit_StorageIdentifier(self, node, ctx):
        # gimme the key for this name in this context
        return str(node.name)
    
    def visit_StorageLocation(self, node, ctx):
        # gimme the value for this key in this context
        name = node.identifier.visit(self, ctx)
        storage = self.getStash(ctx, name)
        return storage.get()

    def visit_DeclStorageLocation(self, node, ctx):
        # I'll store values in this name in this context with this key and type
        name = node.identifier.visit(self, ctx)
        if name in ctx:
            raise
        self.setStash(ctx, name, Storage(node._type, node.const))
        return name
    
    def visit_FuncCall(self, node, ctx):
        raise NotImplementedError
    
    def visit_FuncDeclStatement(self, node, ctx):
        raise NotImplementedError
    
    def visit_AssignStatement(self, node, ctx):
        # Store a value in the locaiton with this name
        name = node.location.visit(self, ctx)
        if node.value is not None:
            value = node.value.visit(self, ctx)
            storage = self.getStash(ctx, name)
            storage.set(value)
        return None

    def visit_PrintStatement(self, node, ctx):
        self.stdout.append(str(node.expr.visit(self, ctx)))

    def visit_ConditionalStatement(self, node, ctx):
        if node.cond.visit(self, ctx):
            node.blockT.visit(self, ctx)
        else:
            node.blockF.visit(self, ctx)
        return None

    def visit_ConditionalLoopStatement(self, node, ctx):
        while node.cond.visit(self, ctx):
            node.block.visit(self, ctx)
        return None

    def visit_ContinueLoopStatement(self, node, ctx):
        raise NotImplementedError

    def visit_BreakLoopStatement(self, node, ctx):
        raise NotImplementedError

    def visit_ExpressionStatement(self, node, ctx):
        return node.statement.visit(self, ctx)

    def visit_ReturnStatement(self, node, ctx):
        raise NotImplementedError

    def visit_BinOp(self, node, ctx):
        lhs = node.left.visit(self, ctx)
        rhs = node.right.visit(self, ctx)
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

    def visit_UnOp(self, node, ctx):
        rhs = node.right.visit(self, ctx)
        if node.op == '!':
            return not rhs
        elif node.op == '+':
            return rhs
        elif node.op == '-':
            return rhs * -1
        else:
            raise

    def visit_ScalarNode(self, node, ctx):
        return node.value

