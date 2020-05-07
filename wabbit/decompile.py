from wabbit.model import ModelVisitor, ConditionalStatement, FuncDeclStatement, ConditionalLoopStatement
from typing import List


def to_wabbit(node):
    decompiler = WabbitDecompiler()
    return node.visit(decompiler, {})


class WabbitDecompiler(ModelVisitor):
    def __init__(self):
        return

    def visit_StorageLocation(self, node, ctx):
        return node.identifier.visit(self, ctx)

    def visit_DeclStorageLocation(self, node, ctx):
        ret = 'const' if node.const else 'var'
        ret += ' ' + node.identifier.name
        if node._type:
            ret += ' ' + str(node._type)
        return ret

    def visit_ScalarNode(self, node, ctx):
        return repr(node.value)

    def visit_AssignStatement(self, node, ctx):
        return node.location.visit(self, ctx) + (' = ' + node.value.visit(self, ctx) if node.value is not None else '') + ';'

    def visit_BinOp(self, node, ctx):
        return ' '.join([node.left.visit(self, ctx), node.op, node.right.visit(self, ctx)])

    def visit_UnOp(self, node, ctx):
        return node.op + node.right.visit(self, ctx)

    def visit_PrintStatement(self, node, ctx):
        return 'print ' + node.expr.visit(self, ctx) + ';'

    def visit_ConditionalStatement(self, node, ctx):
        ret = []
        ret.append('if ' + node.cond.visit(self, ctx) + ' {')
        for line in node.blockT.visit(self, ctx):
            ret.append("\t" + line)
        ret.append('} else {')
        for line in node.blockF.visit(self, ctx):
            ret.append("\t" + line)
        ret.append('}')
        return ret

    def visit_ConditionalLoopStatement(self, node, ctx):
        ret = []
        ret.append('while ' + node.cond.visit(self, ctx) + ' {')
        for line in node.block.visit(self, ctx):
            ret.append("\t" + line)
        ret.append('}')
        return ret

    def visit_BlockExpression(self, node, ctx):
        return '{ ' + ' '.join(node.block.visit(self, ctx)) + ' }'

    def visit_ExpressionStatement(self, node, ctx):
        return node.statement.visit(self, ctx) + ';'

    def visit_FuncCall(self, node, ctx):
        args = ', '.join(arg.visit(self, ctx) for arg in node.args)
        return node.name + '(' + args + ')'

    def visit_FuncDeclStatement(self, node, ctx):
        ret = []
        args = []
        for arg in node.args:
            args.append(' '.join(arg))
        ret.append('func ' + node.name + '(' + ', '.join(args) + ') ' + node.retval + ' {')
        for line in self.to_source(node.body, inner=True):
            ret.append("\t" + line)
        ret.append('}')
        return ret

    def visit_ReturnStatement(self, node, ctx):
        return 'return ' + node.retval.visit(self, ctx) + ';'

    def visit_Statements(self, node, ctx):
        ret = []
        for stmt in node.statements:
            code = stmt.visit(self, ctx)
            if isinstance(code, list):
                ret.extend(code)
            else:
                ret.append(code)
        return ret

    def visit_Program(self, node, ctx): 
        return '\n'.join(node.statements.visit(self, ctx))

    def visit_Grouping(self, node, ctx):
        return '(' + node.expr.visit(self, ctx) + ')'

    def visit_StorageIdentifier(self, node, ctx):
        return str(node.name)
