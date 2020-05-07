from collections import ChainMap
import itertools

from typeguard import typechecked

from .model import Node, Statements


TEMPLATE = """
#include <stdio.h>
#include <stdlib.h>

int main(int argv, char **argv) {{
{declarations}
{instructions}
}}
"""


WB_TYPE_TO_C_TYPE = {
    "int": "int",
    "float": "float",
    "char": "char",
}


class CFunction:
    def __init__(self):
        self.name_counter = itertools.count()
        self._c_names = {}
        self.instructions = []
        self.declarations = []

    @typechecked
    def compile(self, node: Node, env: ChainMap):
        method_name = "compile_" + node.__class__.__name__
        getattr(self, method_name)(node, env)

    def write_source(self):
        indent = "    "
        return TEMPLATE.format(
            declarations="\n".join(indent + decl for decl in self.declarations),
            instructions="\n".join(indent + instr for instr in self.instructions),
        )

    def compile_Statements(self, node: Statements, env):
        for statement in node.statements:
            self.compile(statement, env)

    def _compile_def(self, node, env):
        if node.type:
            self._compile_def_with_type(node, env)
        else:
            self._compile_def_without_type(node, env)

    compile_ConstDef = _compile_def
    compile_VarDef = _compile_def

    def _compile_def_with_type(self, node, env):
        c_type = WB_TYPE_TO_C_TYPE[node.type]
        c_name = self._get_or_create_name(node, prefix=c_type)
        self.declarations.append(f"{c_type} {c_name};")
        if node.value:
            self.instructions.append(f"{c_name} = {node.value};")

    def _compile_def_without_type(self, node, env):
        c_name = self._get_or_create_name(node)
        assert node.value
        self.instructions.append(f"{c_name} = {node.value};")

    def _get_or_create_name(self, node, prefix="", should_exist=None):
        if id(node) not in self._c_names:
            assert should_exist != True, node
            self._c_names[uid] = f"_{prefix}_{next(self.name_counter)}"
        return self._c_names[uid]


def compile_program(model):
    env: ChainMap = ChainMap()
    c_function = CFunction()
    c_function.compile(model, env)
    return c_function.write_source()


def main(filename):
    from .parse import parse_file
    from .typecheck import check_program

    model = parse_file(filename)
    check_program(model)
    code = compile_program(model)
    with open("out.c", "w") as file:
        file.write(code)
    print("Wrote: out.c")


if __name__ == "__main__":
    import sys

    main(sys.argv[1])
