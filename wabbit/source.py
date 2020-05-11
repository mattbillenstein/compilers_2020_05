import os
import sys

from .model import Node
from .parse import parse

NoneType = type(None)

class SourceVisitor:
    def visit(self, node, container=None):
        if node is None:
            return ''
        m = getattr(self, f'visit_{node.__class__.__name__}')
        s = m(node)
        if container:
            s = container % (s)
        return s

    def visit_Name(self, node):
        return node.value

    def visit_Attribute(self, node):
        return f'{self.visit(node.name)}.{node.attr}'

    def visit_Type(self, node):
        return node.type

    def visit_Integer(self, node):
        return f'{node.value}'

    def visit_Float(self, node):
        return f'{node.value}'

    def visit_Bool(self, node):
        return f'{node.value}'.lower()

    def visit_Break(self, node):
        return 'break'

    def visit_Char(self, node):
        return f"'{node.value}'"

    def visit_BinOp(self, node):
        return f'{self.visit(node.left)} {node.op} {self.visit(node.right)}'

    def visit_UnaOp(self, node):
        return f'{node.op}{self.visit(node.arg)}'

    def visit_Block(self, node):
        L = []
        for stmt in node.statements:
            s = self.visit(stmt) + ('' if stmt.is_statement else ';')
            # hack, split lines to add indent, then rejoin them...
            lines = [node.indent + _ for _ in s.split('\n')]
            s = '\n'.join(lines)
            L.append(s)
        return '\n'.join(L) + '\n'

    def visit_Print(self, node):
        return f'print {self.visit(node.arg)}'

    def visit_Const(self, node):
        type = self.visit(node.type, ' %s')
        return f'const {self.visit(node.name)}{type} = {self.visit(node.arg)}'

    def visit_Var(self, node):
        arg = self.visit(node.arg, ' = %s')
        type = self.visit(node.type, ' %s')
        return f'var {self.visit(node.name)}{type}{arg}'

    def visit_Assign(self, node):
        return f'{self.visit(node.name)} = {self.visit(node.arg)}'

    def visit_If(self, node):
        els = self.visit(node.eblock, ' else {\n%s}')
        return f'if {self.visit(node.cond)} {{\n{self.visit(node.block)}}}{els}'

    def visit_While(self, node):
        return f'while {self.visit(node.cond)} {{\n{self.visit(node.block)}}}'

    def visit_Compound(self, node):
        s = '; '.join(self.visit(_) for _ in node.statements) + ';'
        return f'{{ {s} }}'

    def visit_Func(self, node):
        args = ', '.join(self.visit(_) for _ in node.args)
        type = self.visit(node.ret_type, ' %s')
        return f'func {self.visit(node.name)}({args}){type} {{\n{self.visit(node.block)}}}\n'

    def visit_ArgDef(self, node):
        # arg of a function call
        return f'{self.visit(node.name)} {self.visit(node.type)}'

    def visit_Field(self, node):
        # field of a struct
        return f'{self.visit(node.name)} {self.visit(node.type)}'

    def visit_Return(self, node):
        return f'return {self.visit(node.value)}'

    def visit_Call(self, node):
        args = ', '.join(self.visit(_) for _ in node.args)
        return f'{self.visit(node.name)}({args})'

    def visit_Struct(self, node):
        fields = '    ' + ';\n    '.join(self.visit(_) for _ in node.fields) + ';\n'
        return f'struct {self.visit(node.name)} {{\n{fields}}}\n'

    def visit_Enum(self, node):
        args = '    ' + ';\n    '.join(self.visit(_) for _ in node.args) + ';\n'
        return f'enum {self.visit(node.name)} {{\n{args}}}\n'

    def visit_Member(self, node):
        type = f'({self.visit(node.type)})' if node.type else ''
        return f'{self.visit(node.name)}{type}'


def to_source(node):
    return SourceVisitor().visit(node)


def compare_source(source, expected):
    if isinstance(source, Node):
        source = to_source(source)

    s = source.strip('\n')
    e = expected.strip('\n')
    if s != e:
        print(repr(s))
        print(repr(e))
        i = 0
        for a, b in zip(s, e):
            if a != b:
                print(' ' * (i+1), '^')
                print(a, b)
                break
            i += len(repr(a)) - 2
        raise ValueError('Mismatched Source')

def source(text):
    return to_source(parse(text))

def main(args):
    if args:
        if os.path.isfile(args[0]):
            with open(args[0]) as file:
                text = file.read()
        else:
            text = args[0]
    else:
        text = sys.stdin.read()

    print(source(text))

if __name__ == '__main__':
    main(sys.argv[1:])
