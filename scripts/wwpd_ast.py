#!/usr/bin/env python3

import ast
import sys

node = ast.parse(sys.argv[1])
print(ast.dump(node))
