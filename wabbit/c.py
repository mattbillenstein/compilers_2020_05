from .model import *


def compile_program(model):
    pass


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
