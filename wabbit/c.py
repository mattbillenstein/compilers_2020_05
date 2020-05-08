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

from functools import singledispatch
from .model import *

#TODO do I need the whole adding the type to the string thing any more?

class S(str):
    def setType(self, varType):
        self.varType = varType
    def getType(self):
        return self.varType

def add_var(env, varName, varType): # TODO OOOOO scope???
    key = 'dict_of_vars'
    if key not in env:
        env[key] = {}
    if varName not in env[key]:
        env[key][varName] = { 'type': varType }
    if varType is not None and env[key][varName]['type'] is None:
        env[key][varName]['type'] = varType

def get_var_type(env, varName):
    key = 'dict_of_vars'
    if key not in env:
        raise Exception(f'get_var_type: env {key} is uninitialized')
    if varName not in env[key]:
        raise Exception(f'get_var_type: env {varName} is uninitialized')
    return env[key][varName]['type']

def make_variable_declarations(env): # TODO OOOOO scope???
    declarations = []
    key = 'dict_of_vars'
    if key in env:
        for varName in env[key]:
            varType = env[key][varName]['type']
            if varType is not None:
                declarations.append(f'{varType} {varName};')
    return '\n'.join(declarations)

def get_type_from_expr(env, expr):
    if isinstance(expr, tuple):
        (var_name, statements) = expr
        expr = var_name
    if hasattr(expr, 'getType'):
        return expr.getType()
    else:
        key = None
        if isinstance(expr, str):
            key = expr
        else:
            key = expr.name.name
        maybe = get_var_type(env, key)
        if maybe is not None:
            return maybe
        else:
            raise Exception(f'get_type_from_expr no type: {expr}')

NAMES_KEY = 'franfranfrannames'
def get_unique_name(env, prefix):
    if NAMES_KEY not in env:
        env[NAMES_KEY] = {}
    if prefix not in env[NAMES_KEY]:
        env[NAMES_KEY][prefix] = -1
    env[NAMES_KEY][prefix] += 1
    return f'{prefix}{env[NAMES_KEY][prefix]}'

def make_temp_var(env, prefix, varType):
    name = get_unique_name(env, prefix)
    add_var(env, name, varType)
    return name

@singledispatch
def ccompile(node, env):
    raise RuntimeError(f"Can't compile {node}")

@ccompile.register(Statements)
def _(node, env):
    statements = []
    for node in node.children:
        what = ccompile(node, env)
        (var_name, child_statements) = (None, None)
        if isinstance(what, tuple):
            (var_name, child_statements) = ccompile(node, env)
        else:
            raise Exception(f'what {what}')
        if child_statements is not None and len(child_statements) > 0 and not isinstance(node, Var):
            statements += child_statements
    return '\n'.join([f'{s};' for s in statements])

@ccompile.register(BinOp)
def _(node, env):
    (right_var_name, right_statements) = ccompile(node.right, env)
    (left_var_name, left_statements) = ccompile(node.left, env)
    statements = right_statements + left_statements
    result_type = get_type_from_expr(env, left_var_name) # TODO it's not always the left type
    var_name = make_temp_var(env, '_BinOp', result_type)

    def withType(s):
        s1 = S(s)
        s1.setType(result_type)
        return s1

    if node.op == '+':
        statements.append(f'{var_name} = {left_var_name} + {right_var_name}')
        return (withType(var_name), statements)
    elif node.op == '*':
        statements.append(f'{var_name} = {left_var_name} * {right_var_name}')
        return (withType(var_name), statements)
    elif node.op == '/':
        statements.append(f'{var_name} = {left_var_name} / {right_var_name}')
        return (withType(var_name), statements)
    elif node.op == '-':
        statements.append(f'{var_name} = {left_var_name} - {right_var_name}')
        return (withType(var_name), statements)
    elif node.op == '<':
        statements.append(f'{var_name} = {left_var_name} < {right_var_name}')
        return (withType(var_name), statements)
    elif node.op == '>':
        statements.append(f'{var_name} = {left_var_name} > {right_var_name}')
        return (withType(var_name), statements)
    elif node.op == '>=':
        statements.append(f'{var_name} = {left_var_name} >= {right_var_name}')
        return (withType(var_name), statements)
    else:
        raise RuntimeError(f'unsupported op: {node.op}')

@ccompile.register(Integer)
def _(node, env):
    var_name = make_temp_var(env, "_I", "int")
    s = S(f'{var_name} = {node.value}')
    s.setType('int')
    return (var_name, [s])

@ccompile.register(Float)
def _(node, env):
    var_name = make_temp_var(env, "_F", "float")
    s = S(f'{var_name} = {node.value}')
    s.setType('float')
    return (var_name, [s])

@ccompile.register(Char)
def _(node, env):
    var_name = make_temp_var(env, "_C", "char")
    s = S(f'{var_name} = {node.value}')
    s.setType('char')
    return (var_name, [s])

@ccompile.register(Boolean)
def _(node, env):
    var_name = make_temp_var(env, "_B", "int")
    val = 0
    if node.value is True:
        val = 1
    s = S(f'{var_name} = {val}')
    s.setType('int')
    return (var_name, [s])

@ccompile.register(Var)
def _(node, env):
    myType = {
        'int': 'int',
        'float': 'float',
        'bool': 'int',
        }[node.myType]
    add_var(env, node.name, myType)
    return (node.name, [])

@ccompile.register(Assign)
def _(node, env):
    (right_var_name, right_statements) = ccompile(node.value, env)
    (left_var_name, left_statements) = ccompile(node.name, env)
    # NOW! wabbit allows typeless vars and you can assign to them, so let's maybe infer type
    # remember we can assume correctness because of the typechecker (haw haw) so let's not even
    # check if there's already a type or anything, and heck let's not even worry about if it was
    # a var or a const.
    myType = get_type_from_expr(env, right_var_name)
    if myType is not None:
        add_var(env, node.name.name, myType) # TODO location name.name
    else:
        raise Exception(f'whoops, doing an assign and dunno the type left:{left} right:{right}')

    statements = right_statements + left_statements
    statements.append(f'{left_var_name} = {right_var_name}')
    return (left_var_name, statements)

@ccompile.register(Variable) # TODO implement location?
def _(node, env):
    return (node.name, [])

@ccompile.register(Const)
def _(node, env):
    name = node.name
    (right_var_name, right_statements) = ccompile(node.value, env)
    add_var(env, name, get_var_type(env, right_var_name))
    statements = right_statements + [f'{node.name} = {right_var_name}']
    return ({node.name}, statements)

@ccompile.register(UnaryOp)
def _(node, env):
    (right_var_name, right_statements) = ccompile(node.right, env)
    var_name = make_temp_var(env, '_UnaryOp', get_var_type(env, right_var_name))
    statements = right_statements + [f'{var_name} = {node.op}{right_var_name}']
    return (var_name, statements)

@ccompile.register(Grouping)
def _(node, env):
    # grouping has already done its job in the model, pass through
    return ccompile(node.node, env)

@ccompile.register(PrintStatement)
def _(node, env):
    (var_name, statements) = ccompile(node.child, env)
    type_child = None
    if isinstance(node.child, Variable):
        type_child = get_var_type(env, node.child.name)
    else:
        if hasattr(var_name, 'getType'):
            type_child = var_name.getType()
        else:
            type_child = get_var_type(env, var_name)
    type_s = None
    if type_child == 'int':
        type_s = '%i\\n'
    elif type_child == 'float':
        type_s = '%lf\\n'
    elif type_child == 'char':
        type_s = '%c'
    else:
        raise RuntimeError(f'unsupported type print: {var_name}, {type_child}')
    statements.append(f'printf("{type_s}", {var_name})')
    return (None, statements)

@ccompile.register(If)
def _(node, env):
    '''
    goto Lcondition;

    Lconsequence:
    {consequence_statements}
    goto Lafter;

    Lcondition:
    {condition_statements}
    if({condition_var_name}) goto Lconsequence;

    Lafter:

    '''
    (cond_var_name, cond_statements) = ccompile(node.condition, env)
    body = ccompile(node.consequence, env) # TODO see the comment on body in While
    l_condition_name = get_unique_name(env, 'Lcondition')
    l_consequence_name = get_unique_name(env, 'Lconsequence')
    l_after_name = get_unique_name(env, 'Lafter')

    s1 = [
        f'goto {l_condition_name};',
        f'''{l_consequence_name}:
{body}
''',
        f'goto {l_after_name};',
        f'{l_condition_name}:',
    ]
    s2 = [
        f'if({cond_var_name}) goto {l_consequence_name};',
        f'{l_after_name}:',
    ]
    return (None, s1 + cond_statements + s2)

@ccompile.register(IfElse)
def _(node, env):
    '''
    goto Lcondition;

    Lconsequence:
    {consequence_statements}
    goto Lafter;

    Lotherwise:
    {otherwise_statements}
    goto Lafter;

    Lcondition:
    {condition_statements}
    if({condition_var_name}) goto Lconsequence;
    goto Lotherwise;

    Lafter:

    '''
    (cond_var_name, cond_statements) = ccompile(node.condition, env)
    consequence = ccompile(node.consequence, env) # TODO see the comment on body in While
    otherwise = ccompile(node.otherwise, env) # TODO see the comment on body in While
    l_condition_name = get_unique_name(env, 'Lcondition')
    l_consequence_name = get_unique_name(env, 'Lconsequence')
    l_otherwise_name = get_unique_name(env, 'Lotherwise')
    l_after_name = get_unique_name(env, 'Lafter')

    s1 = [
        f'goto {l_condition_name};',
        f'''{l_consequence_name}:
{consequence}
''',
        f'goto {l_after_name};',
        f'''{l_otherwise_name}:
{otherwise}
''',
        f'goto {l_after_name};',
        f'{l_condition_name}:',
    ]
    s2 = [
        f'if({cond_var_name}) goto {l_consequence_name};',
        f'goto {l_otherwise_name};',
        f'{l_after_name}:',
    ]
    return (None, s1 + cond_statements + s2)

@ccompile.register(While)
def _(node, env):
    (condition_var_name, condition_statements) = ccompile(node.condition, env)
    body = ccompile(node.body, env) # this is a statements node, it's a string when compiled... should that be different???? TODO for now just lump it in with the Lwhilebody, but yeah. it should be different
    label_while_body = get_unique_name(env, 'L')
    label_condition = get_unique_name(env, 'Lcondition')
    statements = []
    statements.append(f'goto {label_condition};')
    statements.append(f'''{label_while_body}:
{body}
''')
    statements.append(f'{label_condition}:')
    statements += condition_statements
    statements.append(f'if ({condition_var_name}) goto {label_while_body};')
    return (None, statements)





# Top-level function to handle an entire program.
def compile_program(model):
    env = { }
    # TODO to handle scope we either want to declare variables at the top of their scope _OR_ come up
    # with unique variable names at compile Var time (and when we look them up we have to know scope)
    ccode = ccompile(model, env)
    variable_declarations = make_variable_declarations(env)
    return f'''
/* TODO_NAME.c */
#include <stdio.h>

int main() {{
{variable_declarations}
{ccode}
return 0;
}}
    '''

def main(filename):
    from .parse import parse_file
    from .typecheck import check_program

    model = parse_file(filename)
    check_program(model)
    code = compile_program(model)
    with open('out.c', 'w') as file:
        file.write(code)
    print('Wrote: out.c')

def compile_file(filename):
    from .parse import parse_file
    model = parse_file(filename)
    code = compile_program(model)
    print(code)

if __name__ == '__main__':
    import sys
    # main(sys.argv[1])
    compile_file(sys.argv[1])


