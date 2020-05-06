from .model import *

def interpret_program(statements):
    # Make the initial environment (a dict)
    env = {}
    stdout = []
    interpreter = Interpreter(env, stdout)
    statements.visit(interpreter)
    return stdout


class Storage():
    def __init__(self, _type, const):
        self._type = _type
        self.const = const

    def assign(self, value):
        self.value = value


class Interpreter(ModelVisitor):
    def __init__(self, env, stdout):
        self.env = env
        self.stdout = stdout

    def visit_Statements(self, node):
        for stmt in node.statements:
            stmt.visit(self)
    
    def visit_Program(self, node):
        return node.statements.visit(self)
    
    def visit_BlockNode(self, node):
        raise NotImplementedError
    
    def visit_StorageIdentifier(self, node):
        return str(node.name)
    
    def visit_StorageLocation(self, node):
        name = node.identifier.visit(self)
        return self.env[name]
    
    def visit_DeclStorageLocation(self, node):
        name = node.identifier.visit(self)
        if name in self.env.keys():
            raise
        self.env[name] = Storage(node._type, node.const)
        return self.visit_StorageLocation(node)
    
    def visit_FuncCall(self, node):
        raise NotImplementedError
    
    def visit_FuncDeclStatement(self, node):
        raise NotImplementedError
    
    def visit_AssignStatement(self, node):
        storage = node.location.visit(self)
        storage.assign(node.value)
        return node.value

    def visit_PrintStatement(self, node):
        self.stdout.append(str(node.expr.visit(self)))

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
        for stmt in node.block:
            ret = stmt.visit(self)
        return ret
    
    def visit_ScalarNode(self, node):
        return node.value
