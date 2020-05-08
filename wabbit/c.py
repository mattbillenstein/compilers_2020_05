# c.py
#
# In this file, we're going to transform Wabbit code to C, using it as
# a kind of low-level machine language. At first glance, this might
# sound somewhat crazy, but it actually makes sense for a number of
# reasons.  First, C compilers are standardized and ubiquitous--being
# available everywhere. Second, C is so minimal in features that you
# can use it at a low-level without having to worry about hidden
# side-effects (i.e., garbage collection, etc.).  You can also abuse
# it all sorts of horrible ways to do unnatural acts of programming
# (useful if making a new language).  Finally, in getting
# your compiler to actually "work", there may be certain runtime
# elements that are quite hard to implement or debug directly with machine
# instructions. Therefore, it might be easier to implement things in C 
# as a first step.
#
# As a preliminary step, please read the short C tutorial at
#
#  https://github.com/dabeaz/compilers_2020_05/wiki/C-Programming-Tutorial
#
# Come back here when you've looked it over.  Our goal is to produce
# low-level C code where you are ONLY allowed to use the 
# the following C features:
#
# 1. You can only declare uninitialized variables.  For example:
# 
#         int x;
#         float y;
#         int z = 2 + 3;     // NO!!!!!!!!
#
#    All variables must be declared before use, at the top of the
#    file or function. Reminder: they are uninitialized.
#
# 2. You can only perform ONE operation at a time. Operations can
#    only involve constants and variabless.  The result of an
#    operation must always be immediately stored in a variable.  For
#    example, to compute 2 + 3 * 4, you might do this:
#
#         int _i1;      /* Temporary variables */
#         int _i2;
#
#         _i1 = 3 * 4;
#         _i2 = 2 + i1;
#
# 3. The only allowed control flow constucts are the following two 
#    statements:
#
#        goto Label;
#        if (_variable) goto Label;
#
#        Label:
#           ... code ...
#
#    No, you don't get "else". And you also don't get code blocks 
#    enclosed in braces { }. 
#
# 4. You may print things with printf().
#
# That's it, those are the only C features you may use.  To help you
# out, Here's a small fragment of Wabbit code that executes a loop:
#
#    /* Sample Wabbit Code */
#    /* Print the first 10 factorials */
#
#    var result = 1;
#    var n = 1;
#
#    while n <= 10 {
#        result = result * n;
#        print result;
#        n = n + 1;
#    }
#
# Here's what the corresponding C code might look like (it can vary
# as long as you object the general rules above):
#
#    #include <stdio.h>
#
#    int result;       
#    int n;
#
#    int main() {
#        int _i1;
#        int _i2;
#        int _i3;
#
#        result = 1;
#        n = 1;
#    L1:
#        _i1 = (n <= 10);
#        if (_i1) goto L2;
#        goto L3;
#    L2:
#        _i2 = result * n;
#        result = _i2;
#        printf("%i\n", result);
#        _i3 = n + 1;
#        n = _i3;
#        goto L1;
#    L3:
#        return 0;
#    }
#         
# One thing to keep in mind... the goal is NOT to produce code for
# humans to read.  Instead, it's to produce code that is minimal and
# which can be reasoned about. There is very little actually happening
# in the above code.  It has calculations and gotos. That is basically
# it.  There is no unseen high-level magic going on. What you see
# it what it is.

# Hints:
# ------
# In the interpreter, you wrote code that just "did the operation"
# right there.  You used Python as the runtime environment.  In the
# type-checker, you wrote code that merely "checked the operation" to
# see if there were any errors.  In this project, you have to do a bit
# of both.  For each object in your model, you're going to write a
# function that *creates* the code for carrying out the operation.
# This will be very similar to the interpreter.  However, in order to
# create this code, you've got to know a few things about types. So,
# that information has to be tracked as well.  In addition, there's
# going to be a bit of extra bookkeeping related to the environment.
# For instance, in the above example, extra "C variables" such as
# "_i1", "_i2" and "_i3" are created to hold temporary values.  You'll
# need to have some way to keep track of that.
#
# Also, one other thing... everything that happens here takes place
# *after* type-checking.  Therefore, you don't need to focus on
# problem related to incorrect programs. Assume that all programs
# are fully correct with respect to their usage of types and names.

from .model import *
from collections import ChainMap

# Need some kind of top-level module that serves as a container
# for everything else (global variables, functions, etc.)
class CModule:
    def __init__(self):
        self.globals = ""   # Global variables
        self.functions = [ ]

    def __str__(self):
        return (self.globals + "\n".join(str(func) for func in self.functions))

# I think you want some kind of "C Function" object that gathers everything
# that's being generated as output.

class CFunction:
    def __init__(self, module, name, parameters, return_type):
        self.module = module
        self.module.functions.append(self)    # Add to module function list
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.locals = ""      # Local variables
        self.statements = ""  # Statements generated
        self.stack = [ ]      # Expression stack

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    def __str__(self):
        parmstr = ','.join(f'{ptype} {pname}' for ptype, pname in self.parameters)
        return (f"{self.return_type} {self.name}({parmstr})" + " {\n" + self.locals + self.statements + "\n}\n")
    
    def tempname(self, node):
        return f'_{id(node)}'

_label_num = 0
def new_label():
    global _label_num
    _label_num += 1
    return f'L{_label_num}'

# Top-level function to handle an entire program.
def compile_program(model):
    env = ChainMap()           # Environment.  To keep track of definitions and things.
    cmod = CModule()           # Container for all of the generated code
    cfunc = CFunction(cmod, '_init', [], 'void')
    compile(model, env, cfunc)

    src = str(cmod)
    # If no main is in environment.  Create one
    if 'main' not in env:
        src += 'int main() { _init(); return 0; }\n'

    return src

# Discussion of how this is supposed to work.  env is an environment where we keep
# track of definitions of things (variables, consts, etc.).   cfunc is an object 
# representing a C function--it is the source code that we're creating.  The
# return value from compile() is going to be a typed value. 

@singledispatch
def compile(node, env, cfunc):
    raise RuntimeError(f"Can't compile {node}")

rule = compile.register

@rule(Statements)
def compile_statements(node, env, cfunc):
    result = None
    for stmt in node.statements:
        compile(stmt, env, cfunc)
        if isinstance(stmt, ExpressionStatement):
            result = cfunc.pop()
        else:
            result = None
    if result:
        cfunc.push(result)

@rule(Integer)
def compile_integer(node, env, cfunc):
    cfunc.push(node.value)

@rule(Char)
def compile_char(node, env, cfunc):
    cfunc.push(ord(node.value))   # -> Convert char -> int

@rule(Float)
def compile_float(node, env, cfunc):
    cfunc.push(node.value)

@rule(Bool)
def compile_bool(node, env, cfunc):
    cfunc.push(int(node.value))

@rule(BinOp)
def compile_binop(node, env, cfunc):
    compile(node.left, env, cfunc)
    compile(node.right, env, cfunc)
    rvalue = cfunc.pop()
    lvalue = cfunc.pop()
    myname = cfunc.tempname(node)    # My name
    cfunc.locals += f'{node.type} {myname};\n'
    cfunc.statements += f'{myname} = {lvalue} {node.op} {rvalue};\n'
    cfunc.push(myname)           # Saving where you put the result

@rule(UnaryOp)
def compile_unaryop(node, env, cfunc):
    compile(node.operand, env, cfunc)
    opvalue = cfunc.pop()
    myname = cfunc.tempname(node)
    cfunc.locals += f'{node.type} {myname};\n'
    cfunc.statements += f'{myname} = {node.op} {opvalue};\n'
    cfunc.push(myname)

@rule(PrintStatement)
def compile_print_statement(node, env, cfunc):
    compile(node.expression, env, cfunc)
    value = cfunc.pop()
    if node.expression.type == 'int':
        cfunc.statements += f'printf("%i\\n", {value});\n'
    elif node.expression.type == 'float':
        cfunc.statements += f'printf("%lf\\n", {value});\n'
    elif node.expression.type == 'char':
        cfunc.statements += f'printf("%c", {value});\n'
    elif node.expression.type == 'bool':
        cfunc.statements += f'printf("%i\\n", {value});\n'

@rule(VarDefinition)
@rule(ConstDefinition)
def compile_var_definition(node, env, cfunc):
    # Still need to track var/const definitions for later use
    # Need to emit a C variable declaration for this of some kind.
    env[node.name] = node    
    # If there is any nesting of environments, it has to be a local variable
    if len(env.maps) > 1:
        cfunc.locals += f'{node.type} {node.name};\n'
    else:
        cfunc.module.globals += f'{node.type} {node.name};\n'

    if node.value:
        compile(node.value, env, cfunc)
        cfunc.statements += f'{node.name} = {cfunc.pop()};\n'

@rule(AssignmentStatement)
def compile_assignment_statement(node, env, cfunc):
    compile(node.expression, env, cfunc)
    cfunc.statements += f'{node.location.name} = {cfunc.pop()};\n'

@rule(LoadLocation)
def compile_load_location(node, env, cfunc):
    cfunc.push(node.location.name)

@rule(Grouping)
def compile_grouping(node, env, cfunc):
    compile(node.expression, env, cfunc)

@rule(Compound)
def compile_compound(node, env, cfunc):
    cfunc.statements += '{\n'
    compile(node.statements, env.new_child(), cfunc)
    cfunc.statements += '}\n'

@rule(ExpressionStatement)
def compile_expression_statement(node, env, cfunc):
    compile(node.expression, env, cfunc)

@rule(IfStatement)
def compile_if_statement(node, env, cfunc):
    compile(node.test, env, cfunc)
    true_label = new_label()
    false_label = new_label()
    merge_label = new_label()
    cfunc.statements += f'if ({cfunc.pop()}) goto {true_label};\n'
    cfunc.statements += f'goto {false_label};\n'
    cfunc.statements += f'{true_label}:\n'
    cfunc.statements += '{\n'
    compile(node.consequence, env.new_child(), cfunc)
    cfunc.statements += '}\n'
    cfunc.statements += f'goto {merge_label};\n'

    cfunc.statements += f'{false_label}:\n'
    cfunc.statements += '{\n'
    compile(node.alternative, env.new_child(), cfunc)
    cfunc.statements += '}\n'
    cfunc.statements += f'goto {merge_label};\n'
    cfunc.statements += f'{merge_label}:;\n'

@rule(WhileStatement)
def compile_while_statement(node, env, cfunc):
    test_label = new_label()
    body_label = new_label()
    exit_label = new_label()
    cfunc.statements += f'{test_label}:\n'
    compile(node.test, env, cfunc)
    cfunc.statements += f'if ({cfunc.pop()}) goto {body_label};\n'
    cfunc.statements += f'goto {exit_label};\n'
    cfunc.statements += f'{body_label}:\n'
    cfunc.statements += '{\n'
    newenv = env.new_child()
    newenv['break'] = exit_label      # Sneaky hack. Put label references in env of loop body
    newenv['continue'] = test_label
    compile(node.body, newenv, cfunc)
    cfunc.statements += '}\n'
    cfunc.statements += f'goto {test_label};\n'
    cfunc.statements += f'{exit_label}:;\n'

@rule(BreakStatement)
def compile_break_statement(node, env, cfunc):
    cfunc.statements += f'goto {env["break"]};\n'

@rule(ContinueStatement)
def compile_continue_statement(node, env, cfunc):
    cfunc.statements += f'goto {env["continue"]};\n'


@rule(FunctionDefinition)
def compile_function_definition(node, env, cfunc):
    env[node.name] = node    
    parameters = [ (parm.type, parm.name) for parm in node.parameters ]
    newfunc = CFunction(cfunc.module, node.name, parameters, node.return_type)

    # Hack.  If 'main', inject a call to _init (need to initialize globals)
    if node.name == 'main':
        newfunc.statements += '_init();\n'

    compile(node.statements, env.new_child(), newfunc)

@rule(ReturnStatement)
def compile_return_statement(node, env, cfunc):
    compile(node.expression, env, cfunc)
    cfunc.statements += f'return {cfunc.pop()};'

@rule(FunctionApplication)
def compile_function_application(node, env, cfunc):
    # Evaluate each argument
    for arg in node.arguments:
        compile(arg, env, cfunc)

    # The arguments are on the stack (they pop in reverse order). 
    args = [ cfunc.pop() for _ in node.arguments ]
    args.reverse()
    myname = cfunc.tempname(node)
    cfunc.locals += f'{node.type} {myname};\n'
    cfunc.statements += f'{myname} = {node.name}({",".join(args)});\n'
    cfunc.push(myname)

def main(filename):
    from .parse import parse_file
    from .typecheck import check_program

    model = parse_file(filename)
    check_program(model)
    code = compile_program(model)
    with open('out.c', 'w') as file:
        file.write("#include <stdio.h>\n")
        file.write("typedef int bool;\n")
        file.write(code)
    print('Wrote: out.c')

if __name__ == '__main__':
    import sys
    main(sys.argv[1])


# Sample conversions
#
#  Wabbit : print 2 + 3*4 + 6;
#
#  C:
#
#  int main() {
#      int t1;     /* Temporaries */
#      int t2;
#      int t3;
#      t1 = 3 * 4;    /* One operation at a time. Must store in a variable */
#      t2 = 2 + t1;   /* Each is a "binop" */
#      t3 = t2 + 6;
#      printf("%i\n", t3);
# }
#
#
# Wabbit:
#  var n int = 1;
#  var value int = 1;
# 
# while n < 10 {
#    value = value * n;
#    print value ;
#    n = n + 1;
# }
#
# C:
#   
#  int n;       /* Global variables */
#  int value; 
#
#  int some_function(int x) {
#     ...
#  } 
#
#  int main() {
#      int t1;
#      int t2;
#      int t3;
#      n = 1;      /* Initialize the variables */
#      value = 1;
#      
#      L1:      /* Label */
#          t1 = n < 10;
#          if (t1) goto L2;
#          goto L3;     /* Get out of while */
#      L2:
#          t2 = value * n;
#          value = t2;
#          printf("%i\n", value);
#          t3 = n + 1;
#          n = t3;
#          goto L1;
#      
#      L3:
#          return;
# }
# 
