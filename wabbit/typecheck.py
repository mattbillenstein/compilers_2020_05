from collections import ChainMap
from dataclasses import dataclass
from .model import Node

from typeguard import typechecked


@dataclass
class TypeChecker:
    @typechecked
    def check(self, node, env: ChainMap):
        method_name = "check_" + node.__class__.__name__
        if method := getattr(self, method_name, None):
            method(node, env)
        else:
            for attr in [
                "left",
                "right",
                "test",
                "then",
                "else_",
                "value",
                "location",
                "expression",
            ]:
                if child := getattr(node, attr, None):
                    self.check(child, env)
            if child := getattr(node, "statements", None):
                for statement in node.statements:  # type: ignore
                    self.check(statement, env)


def check_program(model):
    env: ChainMap = ChainMap()
    return TypeChecker().check(model, env)


def main(filename):
    from .parse import parse_file

    model = parse_file(filename)
    check_program(model)


if __name__ == "__main__":
    import sys

    main(sys.argv[1])
