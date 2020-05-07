# run wb programs
#
# Using the parser and the interpreter to run Wabbit programs
# from source

from collections import ChainMap

from wabbit.interp import interpret
from wabbit.parse import parse_source

path = "tests/Script/%s.wb"

fact = "fact"
floattest = "floattest"
inttest = "inttest"


with open(path % inttest) as f:
    source = f.read()

model = parse_source(source)
env = ChainMap()
interpret(model, env)
