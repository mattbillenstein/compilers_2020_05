from wabbit.model import ModelVisitor, ConditionalStatement, FuncDeclStatement, ConditionalLoopStatement
from typing import List


def to_wabbit(node):
    decompiler = WabbitDecompiler()
    return node.visit(decompiler)


class WabbitDecompiler(ModelVisitor):
    def __init__(self):
        return

    def visit_StorageLocation(self, node):
        return node.identifier.visit(self)

    def visit_DeclStorageLocation(self, node):
        ret = 'const' if node.const else 'var'
        ret += ' ' + node.identifier.name
        if node._type:
            ret += ' ' + str(node._type)
        return ret

    def visit_ScalarNode(self, node):
        return repr(node.value)

    def visit_AssignStatement(self, node):
        return node.location.visit(self) + (' = ' + node.value.visit(self) if node.value is not None else '') + ';'

    def visit_BinOp(self, node):
        return ' '.join([node.left.visit(self), node.op, node.right.visit(self)])

    def visit_UnOp(self, node):
        return node.op + node.right.visit(self)

    def visit_PrintStatement(self, node):
        return 'print ' + node.expr.visit(self) + ';'

    def visit_ConditionalStatement(self, node):
        ret = []
        ret.append('if ' + node.cond.visit(self) + ' {')
        for line in node.blockT.visit(self):
            ret.append("\t" + line)
        ret.append('} else {')
        for line in node.blockF.visit(self):
            ret.append("\t" + line)
        ret.append('}')
        return ret

    def visit_ConditionalLoopStatement(self, node):
        ret = []
        ret.append('while ' + node.cond.visit(self) + ' {')
        for line in node.block.visit(self):
            ret.append("\t" + line)
        ret.append('}')
        return ret

    def visit_BlockExpression(self, node):
        return '{ ' + ' '.join(node.block.visit(self)) + ' }'

    def visit_ExpressionStatement(self, node):
        return node.statement.visit(self) + ';'

    def visit_FuncCall(self, node):
        args = ', '.join(arg.visit(self) for arg in node.args)
        return node.name + '(' + args + ')'

    def visit_FuncDeclStatement(self, node):
        ret = []
        args = []
        for arg in node.args:
            args.append(' '.join(arg))
        ret.append('func ' + node.name + '(' + ', '.join(args) + ') ' + node.retval + ' {')
        for line in self.to_source(node.body, inner=True):
            ret.append("\t" + line)
        ret.append('}')
        return ret

    def visit_ReturnStatement(self, node):
        return 'return ' + node.retval.visit(self) + ';'

    def visit_Statements(self, node, inner=False):
        ret = []
        for stmt in node.statements:
            code = stmt.visit(self)
            if isinstance(code, list):
                ret.extend(code)
            else:
                ret.append(code)
        return ret

    def visit_Program(self, node): 
        return '\n'.join(node.statements.visit(self))

    def visit_Grouping(self, node):
        return '(' + node.expr.visit(self) + ')'

    def visit_StorageIdentifier(self, node):
        return str(node.name)
