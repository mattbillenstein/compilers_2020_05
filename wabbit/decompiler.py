from wabbit.model import ModelVisitor, ConditionalStatement, FuncDeclStatement, ConditionalLoopStatement
from typing import List


class Decompiler(ModelVisitor):
    def __init__(self):
        return

    def visit_Location(self, node):
        return node.identifier

    def visit_DeclLocation(self, node):
        ret = 'const' if node.const else 'var'
        ret += ' ' + node.identifier
        if node._type:
            ret += ' ' + str(node._type)
        return ret

    def visit_ScalarNode(self, node):
        return repr(node.value)

    def visit_AssignStatement(self, node):
        return node.location.visit(self) + ' = ' + node.expr.visit(self)

    def visit_BinOp(self, node):
        return ' '.join([node.left.visit(self), node.op, node.right.visit(self)])

    def visit_UnOp(self, node):
        return node.op + node.right.visit(self)

    def visit_PrintStatement(self, node):
        return 'print ' + node.expr.visit(self)

    def visit_ConditionalStatement(self, node):
        ret = 'if ' + node.cond.visit(self) + ' {\n'
        ret += self.to_source(node.blockT, indent=1) 
        ret += '} else {\n'
        ret += self.to_source(node.blockF, indent=1)
        ret += '}'
        return ret

    def visit_ConditionalLoopStatement(self, node):
        ret = 'while ' + node.cond.visit(self) + ' {\n'
        ret += self.to_source(node.block, indent=1)
        ret += '}'
        return ret

    def visit_BlockExpression(self, node):
        return '{ ' + self.to_source(node.block, indent=0, joiner='; ') + '}'

    def visit_ExpressionStatement(self, node):
        return node.statement.visit(self)

    def visit_FuncCall(self, node):
        args = ', '.join(self.visit(arg) for arg in node.args)
        return node.name + '(' + args + ')'

    def visit_FuncDeclStatement(self, node):
        args = []
        for arg in node.args:
            args.append(' '.join(arg))
        return 'func ' + node.name + '(' + ', '.join(args) + ') ' + node.retval + ' {\n' + self.to_source(node.body, indent=1) + '}'

    def visit_ReturnStatement(self, node):
        return 'return ' + node.retval.visit(self)

    def to_source(self, block, indent=0, joiner=';\n'):
        if not isinstance(block, list):
            return block.visit(self)
        ret = ''
        for node in block:
            ret += indent * '\t'
            ret += node.visit(self)
            if isinstance(node, (FuncDeclStatement, ConditionalStatement, ConditionalLoopStatement)):
                ret += '\n'
            else:
                ret += joiner
        return ret
