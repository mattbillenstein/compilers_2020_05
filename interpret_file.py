from wabbit.parse import parse_file
from wabbit.interp import interpret_program

if __name__ == '__main__':
    import sys
    model = parse_file(sys.argv[1])
    interpret_program(model)
