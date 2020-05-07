# run wb programs
#
# Using the parser and the interpreter to run Wabbit programs
# from source

from collections import ChainMap

from wabbit.interp import interpret
from wabbit.parse import parse_source

path = "tests/Script/%s.wb"

chartest = "chartest"
cond = "cond"
fact = "fact"
fib = "fib"
floattest = "floattest"
inttest = "inttest"
mandel_loop = "mandel_loop"

with open(path % mandel_loop) as f:
    source = f.read()

model = parse_source(source)
env = ChainMap()
interpret(model, env)
