from wabbit.model import *

def to_source(node, indent=0, joiner=';\n'):
    if isinstance(node, list):
        # list of statements
        ret = ''
        for n in node:
            ret += indent * '\t'
            ret += to_source(n)
            if isinstance(n, (FuncDeclStatement, ConditionalStatement)):
                ret += '\n'
            else:
                ret += joiner
        return ret
    else:
        # individual statement
        if isinstance(node, ReturnStatement):
            return 'return ' + to_source(node.retval)
        if isinstance(node, FuncDeclStatement):
            args = []
            for arg in node.args:
                args.append(' '.join(arg))
            return 'func ' + node.name + '(' + ', '.join(args) + ') ' + node.retval + ' {\n' + to_source(node.body, indent=1) + '}'
        if isinstance(node, Location):
            if isinstance(node, DeclLocation):
                ret = 'const' if node.const else 'var'
                ret += ' ' + node.identifier
                if node._type:
                    ret += ' ' + str(node._type)
                return ret
            else:
                return node.identifier
        if isinstance(node, ScalarNode):
            return repr(node.value)
        if isinstance(node, AssignStatement):
            return to_source(node.location) + ' = ' + to_source(node.expr)
        if isinstance(node, BinOp):
            return f'{to_source(node.left)} {node.op} {to_source(node.right)}'
        if isinstance(node, UnOp):
            return f'{node.op}{to_source(node.right)}'
        if isinstance(node, PrintStatement):    
            return f'print {to_source(node.expr)}'
        if isinstance(node, ConditionalStatement):
            ret = 'if ' + to_source(node.cond) + ' {\n'
            ret += to_source(node.blockT, indent=1) 
            ret += '} else {\n'
            ret += to_source(node.blockF, indent=1)
            ret += '}'
            return ret
        if isinstance(node, ConditionalLoopStatement):
            ret = 'while ' + to_source(node.cond) + ' {\n'
            ret += to_source(node.block, indent=1)
            ret += '}'
            return ret
        if isinstance(node, BlockExpression):
            return '{ ' + to_source(node.block, indent=0, joiner='; ') + '}'
        if isinstance(node, ExpressionStatement):
            return to_source(node.statement)
        if isinstance(node, FuncCall):
            args = ', '.join(to_source(arg) for arg in node.args)
            return node.name + '(' + args + ')'
        if isinstance(node, ReturnStatement):
            return 'ReturnStatement(' + str(node.retval) + ')'
        return ''
