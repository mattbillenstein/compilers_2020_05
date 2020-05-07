from .model import *


def to_minc(program: Program):
    # Make the initial environment (a dict)
    ctx = {}
    compiler = MinCCompiler()
    program.visit(compiler, ctx)
    return compiler.csrc


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


class MinCCompiler(ScopeAwareModelVisitor):
    '''
    This Wabbit-to-C Compiler is implemented as a ScopeAwareModelVisitor which evaluates wabbit, transpiling into
    C fragments, and propgating up tuples of (type, c-code) to each node to assist in transpilation.

    The minimalist flavor of C produced by this compiler has the following constraints:
        * Only one operation per line
        * Only use goto for control flow
    '''
    def __init__(self):
        self.csrc = []
        self.ctr = 0
        self.stack = []

    def next_cvar(self):
        self.ctr += 1
        return 't' + str(self.ctr)

    def visit_StorageIdentifier(self, node, ctx):
        # gimme the key for this name in this context
        return (None, str(node.name))
    
    def visit_StorageLocation(self, node, ctx):
        # gimme the type for the key in this context
        idtype, idname = node.identifier.visit(self, ctx)
        storage = self.getStash(ctx, idname)
        return (storage._type, idname)
    
    def visit_DeclStorageLocation(self, node, ctx):
        # I'll store values in this name in this context with this key and this type
        name = node.identifier.name
        if name in ctx:
            raise
        if node._type is None and node.value is None:
            raise
        type = node._type
        value = None
        if node.value is not None:
            type, value = node.value.visit(self, ctx)
            if node._type is not None and node._type != type:
                raise
        self.setStash(ctx, name, Storage(type, node.const))
        ret = 'const' if node.const else 'var'
        ret += ' ' + name
        ret += ' ' + str(type) 
        if value is not None:
            self.csrc.append(ret + ' = ' + value + ';')
        else:
            self.csrc.append(ret + ';')
        return (node._type, node.identifier.name)

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
    
    def visit_AssignStatement(self, node, ctx):
        # Store a value in the locaiton with this name
        loctype, locname = node.location.visit(self, ctx)
        if node.value is not None:
            exprtype, exprval = node.value.visit(self, ctx)
            self.csrc.append(locname + ' = ' + exprval + ';')
        return (None, None)
    
    def visit_PrintStatement(self, node, ctx):
        exprtype, exprval = node.expr.visit(self, ctx)
        fmt = exprtype
        if exprtype == 'int':
            fmt = '%i'
        elif exprtype == 'float':
            fmt = '%f'
        elif exprtype == 'char':
            fmt = '%f'
        else:
            raise Exception('idk', exprtype)
        self.csrc.append('printf("' + fmt + '\\n", ' + exprval + ');')
        return (None, None)
    
    def visit_ConditionalStatement(self, node, ctx):
        condtype, condval = node.cond.visit(self, ctx)
        self.csrc.append('if (' + condval + ') {')
        node.blockT.visit(self, ctx)
        self.csrc.append('} else {')
        node.blockF.visit(self, ctx)
        self.csrc.append('}')
        return (None, None)
    
    def visit_ConditionalLoopStatement(self, node, ctx):
        ret = []
        ret.append('while ' + node.cond.visit(self, ctx) + ' {')
        for line in node.block.visit(self, ctx):
            ret.append("\t" + line)
        ret.append('}')
        return ret
    
    def visit_ContinueLoopStatement(self, node, ctx):
        return None
    
    def visit_BreakLoopStatement(self, node, ctx):
        return None
    
    def visit_ExpressionStatement(self, node, ctx):
        exprtype, exprval = node.statement.visit(self, ctx)
        self.csrc.append(exprval + ';')
    
    def visit_ReturnStatement(self, node, ctx):
        return None
    
    def visit_BinOp(self, node, ctx):
        lefttype, leftexpr = node.left.visit(self, ctx)
        righttype, rightexpr = node.right.visit(self, ctx)
        result_type = binop_typemap[(node.op, lefttype, righttype)]
        cvar = self.next_cvar()
        self.csrc.append(''.join([cvar, ' = ', leftexpr, ' ', node.op, ' ', rightexpr, ';']))
        return (result_type, cvar)
    
    def visit_UnOp(self, node, ctx):
        righttype, rightexpr = node.right.visit(self, ctx)
        result_type = unop_typemap[(node.op, righttype)]
        cvar = self.next_cvar()
        self.csrc.append(''.join([cvar, ' = ', node.op, ' ', rightexpr, ';']))
        return (result_type, cvar)
    
    def visit_BlockExpression(self, node, ctx):
        return '{ ' + ' '.join(node.block.visit(self, ctx)) + ' }'
    
    def visit_Int(self, node, ctx):
        return ('int', str(node.value))
    
    def visit_Char(self, node, ctx):
        return ('char', str(ord(node.value)))
    
    def visit_Float(self, node, ctx):
        return ('float', str(node.value))
