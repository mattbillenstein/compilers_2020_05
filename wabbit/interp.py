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
import copy
from collections import UserDict
from collections import deque
from contextlib import contextmanager

logger = logging.getLogger(__name__)

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
    "<": operator.le,
    ">=": lambda a, b: operator.eq(a, b) or operator.gt(a, b),
    "<=": lambda a, b: operator.eq(a, b) or operator.lt(a, b),
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
        logger.debug("Tearing down env")
        assert len(self._scopes) > 1
        self._scopes.popleft()

    def __setitem__(self, key, value):
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
    leftval = interpret(left, env)
    rightval = interpret(right, env)
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
    name = assignment_node.location.name  # will probably have to change for structs
    value_expr = assignment_node.value
    value = interpret(value_expr, env)
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
        for statement in clause_node.statements:
            interpret(statement, env)


@interpret.register(WhileLoop)
def interpret_while_loop_node(while_loop_node: WhileLoop, env: Environment):
    logger.debug(f"Interpreting while loop {repr(while_loop_node)}")
    condition = while_loop_node.condition
    body = while_loop_node.body

    while True:
        condition_result = interpret(condition, env)
        if not isinstance(condition_result, bool):
            raise RuntimeError(
                f"Expected bool from Condition result. Got {type(condition_result)}"
            )
        if condition_result is True:
            logger.debug(f"Condition evaluated True, executing body: {repr(body)}")
            interpret(body, env)
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
    value = interpret(expr)
    if op == '+':
        return value
    elif op == '-':
        return value * -1
    else:
        raise RuntimeError(f'Unexpected unary operator: "{op}"')