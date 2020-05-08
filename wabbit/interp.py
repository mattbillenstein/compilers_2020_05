# interp.py
#
# In order to write a compiler for a programming language, it helps to
# have some kind of specification of how programs written in the
# programming language are actually supposed to work. A language is
# more than just "syntax" or a data model.  There has to be some kind
# of operational semantics that describe what happens when a program
# runs.
#
# One way to specify the operational semantics is to write a so-called
# "definitional interpreter" that directly executes the data
# model. This might seem like cheating--after all, our final goal is
# not to write an interpreter, but a compiler. However, if you can't
# write an interpreter, chances are you can't write a compiler either.
# So, the purpose of doing this is to pin down fine details as well as
# our overall understanding of what needs to happen when programs run.
#
# We'll write our interpreter in Python.  The idea is relatively
# straightforward.  For each class in the model.py file, you're
# going to write a function similar to this:
#
#    def interpret_node_name(node, env):
#        # Execute "node" in the environment "env"
#        ...
#        return result
#
# The input to the function will be an object from model.py (node)
# along with an object respresenting the execution environment (env).
# The function will then execute the node in the environment and return
# a result.  It might also modify the environment (for example,
# when executing assignment statements, variable definitions, etc.).
#
# For the purposes of this projrect, assume that all programs provided
# as input are "sound"--meaning that there are no programming errors
# in the input.  Our purpose is not to create a "production grade"
# interpreter.  We're just trying to understand how things actually
# work when a program runs.
#
# For testing, try running your interpreter on the models you
# created in the example_models.py file.
#
from functools import singledispatch
from .model import *
import operator
import logging
import ast
from collections import UserDict
from collections import deque
from contextlib import contextmanager
from typing import NamedTuple
from collections import namedtuple
from typing import TypeVar
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
#logger.addHandler(logging.StreamHandler(sys.stdout))

# Top level function that interprets an entire program. It creates the
# initial environment that's used for storing variables.
#logging.basicConfig(level=logging.DEBUG)


def wabbit_divide(a, b):
    if isinstance(a, int) and isinstance(b, int):
        return operator.floordiv(a, b)
    elif isinstance(a, float) or isinstance(b, float):
        return operator.truediv(a, b)
    else:
        raise RuntimeError(f'Cannot divide objects of type "{type(a)}" and "{type(b)}"')


OPERATIONS = {
    "+": operator.add,
    "-": operator.sub,
    "/": wabbit_divide,
    "*": operator.mul,
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    '||': lambda a, b: bool(operator.or_(a, b)),
    '&&': lambda a, b: bool(operator.and_(a, b)),
}


class Environment(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._scopes = deque()
        self._scopes.append(self)

    @property
    def _closest_scope(self):
        return self._scopes[0]

    def _child_env(self):
        logger.debug("Creating child env")
        new_env = dict()
        self._scopes.appendleft(new_env)
        return self

    @contextmanager
    def child_env(self):
        try:
            env = self._child_env()
            yield env
        finally:
            self._teardown_env()

    def _teardown_env(self):
        assert len(self._scopes) > 1
        sc = self._scopes.popleft()
        logger.debug(f"Tore down env: {sc}")


    def __setitem__(self, key, value):
        logger.debug(f'Setting key {repr(key)} to value {repr(value)}')
        if isinstance(value, Node):
            logger.debug("!!! Node has been set in environment !!!")
        for scope in list(self._scopes):
            # first check for existing declarations of a variable
            if key in scope:
                if scope is self:
                    #  avoid recursion
                    super().__setitem__(key, value)
                else:
                    scope[key] = value
                return
        else:
            #  If the name isn't in any existing scope, create it in the closest scope
            if self._closest_scope is self:
                super().__setitem__(key, value)
            else:
                self._closest_scope[key] = value
            return

    def __getitem__(self, item):
        for scope in self._scopes:
            if item in scope:
                if scope is self:
                    return super().__getitem__(item)
                else:
                    return scope[item]
        raise KeyError(item)

    def declare(self, key, value):
        """
        Declarations (e.g. var foo | const foo) should always go to the closest scope
        """
        if not self._closest_scope is self:
            logger.debug(f'Setting key {repr(key)} to value {repr(value)}')
        self._closest_scope[key] = value

    def globals(self):
        return dict(self.items())

    def locals(self):
        locals_ = dict()
        for scope in reversed(self._scopes):
            locals_.update(scope)
        return locals_

    def __repr__(self):
        return (
            "".join(repr(scope) for scope in list(self._scopes)[:-1])
            + super().__repr__()
        )


class BreakEncountered(RuntimeError):
    # Maybe raise this for break statements
    # Catch where legal
    ...


class ContinueEncountered(RuntimeError):
    # Maybe raise this for continue statements
    # Catch where legal
    ...

class ReturnEncountered(RuntimeError):
    ...

def interpret_program(model):
    # Make the initial environment (a dict)
    env = Environment()
    interpret(model, env)


# Internal function to interpret a node in the environment
@singledispatch
def interpret(node, env):
    # Expand to check for different node types
    ...
    raise RuntimeError(f"Can't interpret {node}")


@interpret.register(Program)
def interpret_program_node(program_node: Program, env: Environment):
    logger.debug(f"Interpreting program node: {repr(program_node)}")
    for statement in program_node.statements:
        logger.debug(f"Interpreting program statement: {repr(statement)}")
        interpret(statement, env)


@interpret.register(BinOp)
def interpret_binop_node(binop_node: BinOp, env: Environment):
    logger.debug(f"Interpreting binop: {repr(binop_node)}")
    op = binop_node.op
    left = binop_node.left
    right = binop_node.right
    logger.debug('Evaluating expressions before op')

    logger.debug(f'Evaluating Left: {repr(left)}')
    leftval = interpret(left, env)
    logger.debug(f'Left value: {repr(leftval)}')
    if op == '&&' and not bool(leftval):
        return False
    elif op == '||' and bool(leftval):
        return True
    logger.debug(f'Evaluating right: {repr(right)}')
    rightval = interpret(right, env)
    logger.debug(f'Right value: {repr(rightval)}')
    operation = OPERATIONS.get(op)
    if not operation:
        raise RuntimeError(f"Cannot interpret operation {op}")
    result = operation(leftval, rightval)
    logger.debug(f"BinOp result: {result}")
    return result


@interpret.register(Compare)
def interpret_compare_node(compare_node: Compare, env: Environment) -> bool:
    logger.debug(f"Interpreting comparison node: {repr(compare_node)}")
    op = compare_node.op
    left = compare_node.left
    right = compare_node.right
    leftval = interpret(left, env)
    rightval = interpret(right, env)
    operation = OPERATIONS.get(op)
    if not operation:
        raise RuntimeError(f"Cannot interpret operation {op}")
    result = operation(leftval, rightval)
    if not isinstance(result, bool):
        raise RuntimeError(
            f"Comparison operation expected to return bool, got {type(result)}"
        )
    logger.debug(f"Comparison result: {result}")
    return result


@interpret.register(Assignment)
def interpret_assignment_node(assignment_node: Assignment, env: Environment):
    logger.debug('Interpreting assignment statement')
    name = assignment_node.location.name  # will probably have to change for structs
    value_expr = assignment_node.value
    value = interpret(value_expr, env)
    logger.debug(f'Assigning name {name} with value {value}')
    env[name] = value


@interpret.register(VariableDefinition)
def interpret_variable_definition_node(
    variable_def_node: VariableDefinition, env: Environment
):
    name = variable_def_node.name
    type_ = variable_def_node.type
    value_expr = variable_def_node.value
    if value_expr is None:
        value = None
    else:
        value = interpret(value_expr, env)
    env.declare(name, value)
    # env[name] = value


@interpret.register(Integer)
def interpret_integer_node(integer_node: Integer, env: Environment):
    return integer_node.value


@interpret.register(Float)
def interpret_float_node(float_node: Float, env: Environment):
    return float_node.value


@interpret.register(ConstDefinition)
def interpret_const_definition(const_def_node: ConstDefinition, env: Environment):
    name = const_def_node.name
    type_ = const_def_node.type
    value_expr = const_def_node.value
    value = interpret(value_expr, env)
    # env[name] = value
    env.declare(name, value)


@interpret.register(PrintStatement)
def interpret_print_statement(print_stmt_node, env):
    expr = print_stmt_node.expression
    value = interpret(expr, env)
    if isinstance(value, str):
        print(value, end='')
    elif isinstance(value, float):
        print(WabbitFloat(value))
    elif isinstance(value, bool):
        print(str(value).lower())
    else:
        print(value)


@interpret.register(Identifier)
def interpret_identifier_node(identifier_node: Identifier, env: Environment):
    name = identifier_node.name  # Probably going to have to change for structs

    return env[name]


@interpret.register(IfStatement)
def interpret_if_statement_node(if_statement_node: IfStatement, env: Environment):
    condition = if_statement_node.condition
    consequent = if_statement_node.consequent
    alternative = if_statement_node.alternative
    condition_result = interpret(condition, env)
    if not isinstance(condition_result, bool):
        raise RuntimeError(
            f"Expected bool from Condition result. Got {type(condition_result)}"
        )
    if condition_result is True:
        interpret(consequent, env)
    elif condition_result is False and alternative is not None:
        interpret(alternative, env)


@interpret.register(Clause)
def interpret_clause_node(clause_node, env: Environment):
    with env.child_env():
        retval = None
        for statement in clause_node.statements:
            retval = interpret(statement, env)
        return retval  # Most callers won't need this, but Compound Expressions do need the last thing

@interpret.register(WhileLoop)
def interpret_while_loop_node(while_loop_node: WhileLoop, env: Environment):
    logger.debug(f"Interpreting while loop {id(while_loop_node)}")
    condition = while_loop_node.condition
    body = while_loop_node.body
    while True:
        condition_result = interpret(condition, env)
        if not isinstance(condition_result, bool):
            raise RuntimeError(
                f"Expected bool from Condition result. Got {type(condition_result)}"
            )
        if condition_result is True:
            logger.debug(f"Condition evaluated True, executing body: {id(while_loop_node)}")
            try:
                interpret(body, env)
            except ContinueEncountered:
                logger.debug('Continue encountered')
                continue
            except BreakEncountered:
                logger.debug('Break encountered')
                break
        else:
            logger.debug("Condition evaluated false, exiting while loop")
            break


@interpret.register(ExpressionStatement)
def interpret_expression_statement_node(expression_statement_node, env):
    expr = expression_statement_node.expression
    return interpret(expr, env)


@interpret.register(UnaryOp)
def interpret_unary_op_node(unary_op_node, env):
    op = unary_op_node.op
    expr = unary_op_node.operand
    value = interpret(expr, env)
    if op == "+":
        return value
    elif op == "-":
        return value * -1
    elif op == '!':
        if not isinstance(value, bool):
            raise RuntimeError(f"Logical NOT (!) expected a bool. Got {type(value)}")
        return not value
    else:
        raise RuntimeError(f'Unexpected unary operator: "{op}"')


@interpret.register(CharacterLiteral)
def interpret_character_literal(character_literal_node, env):
    s = ast.literal_eval(character_literal_node.value)
    if len(s) != 1:
        raise RuntimeError(f"Character literal of unexpected length > 1: {repr(s)}")
    return s


@interpret.register(BreakStatement)
def interpret_break_statement(_, __):
    raise BreakEncountered(
        "break statement encountered. If this bubbles up to you, it's an error due to illegal usage. "
        "Did you use break outside a while loop?"
    )


@interpret.register(ContinueStatement)
def interpret_continue_statement(_, __):
    raise ContinueEncountered(
        "continue statement encountered. If this bubbles up to you, it's an error due to illegal usage. "
        "Did you use continue outside a while loop?"
    )


@interpret.register(ReturnStatement)
def interpret_return_statement(return_statement_node, env):
    return_expr = return_statement_node.expression
    retval = interpret(return_expr, env)

    # Hack to make sure illegal usage of return is not used
    logger.debug(f'raising return encountered with piggybacked value: {repr(retval)}')
    raise ReturnEncountered(
        "return statement encountered. If this bubbles up to you, it's an error due to illegal usage. "
        "Did you use continue outside a while loop?",
        retval
    )


@interpret.register(Parameter)
def interpret_param_node(param_node, env):
    Param = namedtuple('Param', ['name', 'type'])
    return Param(param_node.name, param_node.type)


@interpret.register(FunctionDefinition)
def interpret_function_definition_node(func_def_node: FunctionDefinition, env):
    env[func_def_node.name] = func_def_node

@interpret.register(StructDefinition)
def interpret_struct_definition_node(struct_def_node, env):
    logger.debug(f"Interpreting struct def {repr(struct_def_node)}")

    env[struct_def_node.name] = struct_def_node

@interpret.register(FunctionOrStructCall)
def interpret_function_call_node(function_or_struct_call_node, env):
    logger.debug("Handling struct/func call")
    obj_name = function_or_struct_call_node.name
    arguments = function_or_struct_call_node.arguments
    func_or_struct = env[obj_name]
    if isinstance(func_or_struct, StructDefinition):
        logger.debug("The call is for a struct")

        struct_def = func_or_struct
        arg_values = []
        # first evaluate the argument expressions
        for arg_expr in arguments:
            arg_values.append(interpret(arg_expr, env))

        struct = NamedTuple(struct_def.name, [(field.name, field.type) for field in struct_def.fields])
        struct_obj = struct(*arg_values)
        return struct_obj

    logger.debug("Call was not a struct, assuming is a function")
    func = func_or_struct
    func_clause = func.body
    # inject argument values into the environment and then run the function clause
    with env.child_env():
        for param, arg_expr in zip(func.parameters, arguments):
            env.declare(key=param.name, value=interpret(arg_expr, env))

        try:
            return interpret(func_clause, env)
        except ReturnEncountered as ret_exception:
            logger.debug('Caught return encoutner exception')
            #  we use a hack of raising an error on return statements
            #  so we pull the return value out of the exception object
            retval = ret_exception.args[1]
            logger.debug(f"retval: {repr(retval)}")
        return retval

#
# @interpret.register(StructField)
# def interpret_struct_field_node(struct_field_node, env):
#     Field = namedtuple("Field", ["name", "type"])
#     f = Field(struct_field_node.name, struct_field_node.type)
#     env[f.name] = f
#     return f
#

@interpret.register(FieldLookup)
def interpret_struct_field_lookup_node(field_lookup_node, env):
    logger.debug(f"Interpreting struct field lookup node: {repr(field_lookup_node)}")
    location = field_lookup_node.location
    struct = interpret(location, env)
    attr = getattr(struct, field_lookup_node.fieldname)
    return attr  # >?



class WabbitStruct(NamedTuple):
    pass

# @interpret.register(StructInstantiate)
# def interpret_struct_instantiation_node(struct_inst_node, env):
#     struct = env[struct_inst_node.struct_name]
#     arguments = struct_inst_node.arguments
#     arg_values = []
#     # first evaluate the argument expressions
#     for arg_expr in arguments:
#         arg_values.append(interpret(arg_expr, env))


@interpret.register(CompoundExpr)
def interpret_compound_expr(compound_expr_node, env):
    return interpret(compound_expr_node.clause, env)

@interpret.register(Grouping)
def interpret_grouping_node(group_node, env):
    logger.debug(f'Interpreting grouping {repr(group_node)}')
    grouping_value = interpret(group_node.expression, env)
    logger.debug(f'Group value: {grouping_value}')
    return grouping_value

@interpret.register(Unit)
def interpret_unit_node(unit_node, env):
    return WabbitUnit()


@interpret.register(Bool)
def interpret_bool_node(bool_node, env):
    return bool_node.value

if __name__ == "__main__":
    #logging.basicConfig(level=logging.DEBUG)
    print('-'*80)
    import sys
    from .parse import parse_file
    if len(sys.argv) != 2:
        raise SystemExit("Usage: wabbit.interp filename")
    model = parse_file(sys.argv[1])
    print(repr(model))
    print(model)
    interpret_program(model)
    print('-'*80)

