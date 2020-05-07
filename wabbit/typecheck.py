from .model import *


def check_program(model):
    env = {}
    check(model, env)


def check(node, env):
    pass


def main(filename):
    from .parse import parse_file

    model = parse_file(filename)
    check_program(model)


if __name__ == "__main__":
    import sys

    main(sys.argv[1])
