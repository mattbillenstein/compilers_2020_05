from .model import *


def interpret_program(statements):
    # Make the initial environment (a dict)
    env = {}
    stdout = []
    interpreter = Interpreter(env, stdout)
    statements.visit(interpreter)
    return stdout

UNDEF = object()

class Storage():
    def __init__(self, _type, const):
        self._type = _type
        self.const = const
        self.value = UNDEF

    def set(self, value):
        self.value = value
        return None

    def get(self):
        if self.value is UNDEF:
            raise RuntimeError()
        return self.value


class Interpreter(ModelVisitor):
    def __init__(self, env, stdout):
        self.env = env
        self.stdout = stdout

    def visit_Statements(self, node):
        for stmt in node.statements:
            stmt.visit(self)
        return None
    
    def visit_Program(self, node):
        node.statements.visit(self)
        return None
    
    def visit_BlockNode(self, node):
        raise NotImplementedError
    
    def visit_StorageIdentifier(self, node):
        # gimme the key for this name in this env
        return str(node.name)
    
    def visit_StorageLocation(self, node):
        # gimme the value for this key
        name = node.identifier.visit(self)
        storage = self.env[name]
        return storage.get()
    
    def visit_DeclStorageLocation(self, node):
        # I'll store values in this name in this env with this key and type
        name = node.identifier.visit(self)
        if name in self.env.keys():
            raise
        self.env[name] = Storage(node._type, node.const)
        return node.identifier.visit(self)
    
    def visit_FuncCall(self, node):
        raise NotImplementedError
    
    def visit_FuncDeclStatement(self, node):
        raise NotImplementedError
    
    def visit_AssignStatement(self, node):
        # Store a value in the locaiton with this name
        name = node.location.visit(self)
        if node.value is not None:
            value = node.value.visit(self)
            storage = self.env[name]
            storage.set(value)
        return None

    def visit_PrintStatement(self, node):
        self.stdout.append(str(node.expr.visit(self)))

    def visit_ConditionalStatement(self, node):
        if node.cond.visit(self):
            node.blockT.visit(self)
        else:
            node.blockF.visit(self)
        return None

    def visit_ConditionalLoopStatement(self, node):
        while node.cond.visit(self):
            node.block.visit(self)
        return None

    def visit_ContinueLoopStatement(self, node):
        raise NotImplementedError

    def visit_BreakLoopStatement(self, node):
        raise NotImplementedError

    def visit_ExpressionStatement(self, node):
        return node.statement.visit(self)

    def visit_ReturnStatement(self, node):
        raise NotImplementedError

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
    
    def visit_BlockExpression(self, node):
        ret = None
        for stmt in node.block.statements:
            ret = stmt.visit(self)
        return ret
    
    def visit_ScalarNode(self, node):
        return node.value
