import io
import os
from functools import singledispatch

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
#    def transpile_node_name(node, env):
#        # Execute "node" in the environment "env"
#        raise NotImplementedError(locals())
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
from recordclass import recordclass
import jinja2
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))
from tempfile import tempdir

# Top level function that interprets an entire program. It creates the
# initial environment that's used for storing variables.
# logging.basicConfig(level=logging.DEBUG)


class Scope(UserDict):
    def __init__(self, *args, **kwargs):
        if 'env' in kwargs:
            self.env = kwargs.pop('env')
        else:
            self.env = self
        super().__init__(*args, **kwargs)
    def get_scoped_cython_name(self, key):
        return Identifier(f'cython_scoped_var_{id(self)}_{key}')

    def __setitem__(self, key, value):
        varname = self.get_scoped_cython_name(key)
        self.env.writeline(f'{varname} = {value}\n')
        super(Scope, self).__setitem__(key, value)


class Environment(Scope):
    def __init__(self, *args, **kwargs):
        self.outfilename = kwargs.pop('outfile')
        super().__init__(*args, **kwargs)
        self._scopes = deque()
        self._scopes.append(self)
        self._const_registry = {}
        self._enum_registry = {}
        self._in_function = 0  # how many nested call stacks we're in
        self._is_function_scope = False
        self.scope_level = 0
        templates_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cython_templates')
        self.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_path), autoescape=False, trim_blocks=True)
        self.__outfilegen = self._outfile()  # avoid closing the file when init ends
        self.outfile = io.StringIO()
        self.boiler = io.StringIO()

    def get_scoped_cython_name(self, key):
        return f'cython_scoped_var_{id(self)}_{key}'

    def _outfile(self):
        with open(self.outfilename, 'w') as f:
            yield f


    @property
    def _closest_scope(self):
        return self._scopes[0]

    @property
    def _closest_function_scope(self):
        for scope in self._scopes:
            if scope._is_function_scope:
                return scope

    def _child_env(self, for_function=False):
        logger.debug("Creating child env")
        new_env = Scope()
        if for_function:
            logger.debug(f'Creating child env for function. Incrementing call stack from {self._in_function} to'
                         f'{self._in_function + 1}')
            self._in_function += 1
        if for_function:  # Hack on "_is_function_scope" -- Used internally only
            logger.debug('Tagging new env with _is_function_scope TRUE')
            new_env._is_function_scope = True
        else:
            logger.debug('Tagging new env with _is_function_scope FALSE')
            new_env._is_function_scope = False
        self._scopes.appendleft(new_env)
        return self

    @property
    def in_function(self):
        """
        Whether or not the
        """
        return bool(self._in_function)

    @contextmanager
    def child_env(self, for_function=False):
        try:
            env = self._child_env(for_function=for_function)
            logger.debug(f"Yielding env with keys: {repr(env.keys())}")
            yield env  # This is normally not used, but might as well send it along
        finally:
            self._teardown_env(for_function=for_function)


    def _teardown_env(self, for_function=False):
        logger.debug("Tearing down env...")
        assert len(self._scopes) > 1, "Attempted to teardown global scope"
        sc = self._scopes.popleft()
        if for_function:
            logger.debug(f'Decrementing call stack count from {self._in_function} to {self._in_function - 1}')
            assert self._in_function > 0
            self._in_function -= 1
        logger.debug(f"Tore down env: {sc}")


    def __setitem__(self, key, value):
        logger.debug(f'Setting key {repr(key)} to value {repr(value)}')
        if isinstance(value, Node):
            logger.debug("!!! Node has been set in environment !!!")
        try:
            scope = self._get_lookup_scope(key)
            if scope is self:
                super().__setitem__(key, value)
                return
            else:
                scope[key] = value
                return
        except KeyError:
            #  If the name isn't in any existing scope, create it in the closest scope
            scope = self._closest_scope
            if scope is self:
                super().__setitem__(key, value)
            else:
                scope[key] = value
            return

    def __getitem__(self, item):
        lookup_scope = self._get_lookup_scope(item)
        if lookup_scope is self:
            return super().__getitem__(item)
        return lookup_scope[item]

    def declare(self, key, value, type_=None):
        """
        Declarations (e.g. var foo | const foo) should always go to the closest scope
        """
        if not self._closest_scope is self:
            logger.debug(f'Setting key {repr(key)} to value {repr(value)}')
        self._closest_scope[key] = value

    def _get_lookup_scope(self, item):
        for scope in self._scopes:
            if item in scope:
                return scope
            if scope._is_function_scope:
                break
        if item in self:
            return self
        raise KeyError(item)

    def globals(self):
        return Scope(self.items())

    def locals(self):
        locals_ = Scope()
        for scope in reversed(self._scopes):
            if scope is self:
                continue  # dont include globals in locals
            if scope._is_function_scope and not scope is self._closest_function_scope:
                break
            locals_.update(scope)
        return locals_

    def __repr__(self):
        return (
            "".join(repr(scope) for scope in list(self._scopes)[:-1])
            + super().__repr__()
        )

    # def write_template(self, template_name, **kwargs):
    #     logger.debug(f'Processing template {template_name} with kwargs: {kwargs}')
    #     template = self.jinja_env.get_template(template_name)
    #     for k, v in kwargs.items():
    #         if not isinstance(v, Node):
    #             logger.warning(f"Template expected str got key {k}: {v}")
    #     part = template.render(**kwargs)
    #     indentation = ' ' * self.scope_level * 4
    #     for line in part.split('\n'):
    #         line = f'{indentation}{line}\n'
    #         self.outfile.write(line)
    #         print(line)

    def writeline(self, text):
        if text is None:
            logger.warning('SKIPPING NONE')
            return
        logger.debug(f'Writing line text: {text}')
        assert not isinstance(text, Node)
        indentation = ' ' * self.scope_level * 4
        self.outfile.write(f'{indentation}{text}')
        print(f'{indentation}{text}')

    def write_out(self, outfile='out.pyx'):
        self.outfile.seek(0)
        with open(outfile, 'w') as f:
            f.write(self.outfile.read())


    def retrieve_scoped_name_from_node(self, node):
        if isinstance(node, Identifier):
            name = node.name
            scope = self._get_lookup_scope(name)
            return scope.get_scoped_cython_name(name)



class BreakEncountered(RuntimeError):
    # Maybe raise this for break statements
    # Catch where legal
    pass


class ContinueEncountered(RuntimeError):
    # Maybe raise this for continue statements
    # Catch where legal
    pass


class ReturnEncountered(RuntimeError):
    pass

def transpile_program(model):
    env = Environment(outfile='out.pyx')
    transpile(model, env)
    env.write_out()

# Internal function to interpret a node in the environment
@singledispatch
def transpile(node, env):
    raise NotImplementedError(locals())


@transpile.register(Program)
def transpile_program_node(program_node: Program, env: Environment):
    for statement in program_node.statements:
        transpile(statement, env)


@transpile.register(BinOp)
def transpile_binop_node(binop_node: BinOp, env: Environment):
    op = binop_node.op
    left = binop_node.left
    right = binop_node.right
    if type(left) not in (Identifier, CharacterLiteral, Float, Integer):
        logger.debug(f"Left BinOp arg was not a known literal was {type(left)}")
        left = transpile(left, env)
    if type(right) not in (Identifier, CharacterLiteral, Float, Integer):
        logger.debug(f"Right BinOp arg was not a known literal was {type(right)}")
        right = transpile(left, env)

    if isinstance(left, Identifier):
        left = env.retrieve_scoped_name_from_node(left)
    if isinstance(right, Identifier):
        right = env.retrieve_scoped_name_from_node(right)

    if op in      (       "+",
            "-",
            "*",
            "/",
            "<",
            "<=",
            ">=",
            ">",
            "==",
            "!=",
        ):
        op = op
    elif op in ('&&', '||'):
        if op == '&&':
            op = 'and'
        elif op == '||':
            op = 'or'
    else:
        raise ValueError(f"Unsupported op: {op}")

    return f'{left} {op} {right}'

@transpile.register(Compare)
def transpile_compare_node(compare_node: Compare, env: Environment) -> bool:
    raise NotImplementedError(locals())

def transpose_type(wabbit_type):
    if wabbit_type == 'int':
        return 'int'

def infer_type(obj):
    if isinstance(obj, CharacterLiteral):
        return 'char'
    logger.debug(f"Can't infer type of object {repr(obj)} ({obj})")
    return

@transpile.register(Assignment)
def transpile_assignment_node(assignment_node: Assignment, env: Environment):
    name = assignment_node.location.name  # will have to adjust for nesting lookups
    rhs = transpile(assignment_node.value, env)
    env[name] = rhs


@transpile.register(VariableDefinition)
def transpile_variable_definition_node(
        variable_def_node: VariableDefinition, env: Environment
):
    name = variable_def_node.name
    type_ = variable_def_node.type
    value_expr = variable_def_node.value
    if value_expr is None:
        value = None
    else:
        value = transpile(value_expr, env)
    env.declare(name, value, type_)



@transpile.register(Integer)
def transpile_integer_node(integer_node: Integer, env: Environment):
    return integer_node.value


@transpile.register(Float)
def transpile_float_node(float_node: Float, env: Environment):
    return float_node.value


@transpile.register(ConstDefinition)
def transpile_const_definition(const_def_node: ConstDefinition, env: Environment):
    name = const_def_node.name
    type_ = const_def_node.type
    value_expr = const_def_node.value
    value = transpile(value_expr, env)
    env.declare(name, value, type_)

    # type_ = const_def_node.type
    # name = const_def_node.name
    # value = const_def_node.value
    # if value is not None:
    #     value = transpile(value, env)  # I think
    #
    # if type_ is None and value is not None:
    #     type_ = infer_type(const_def_node.value)
    # if type_  and len(value) == 1:
    #     value = repr(value)
    # env.write_template('const_definition.jinja2', type=type_, name=name, value=value)





@transpile.register(PrintStatement)
def transpile_print_statement(print_stmt_node, env):
    expr = print_stmt_node.expression
    value = transpile(expr, env)
    if isinstance(value, str):
        print(value, end='')
    elif isinstance(value, float):
        print(WabbitFloat(value))
    elif isinstance(value, bool):
        print(str(value).lower())
    else:
        print(value)

    env.writeline(f'print({value})\n')

@transpile.register(Identifier)
def transpile_identifier_node(identifier_node: Identifier, env: Environment):
    name = identifier_node.name
    return env[name]

@transpile.register(IfStatement)
def transpile_if_statement_node(if_statement_node: IfStatement, env: Environment):
    condition = if_statement_node.condition
    consequent = if_statement_node.consequent
    alternative = if_statement_node.alternative
    condition_result = transpile(condition, env)
    # if not isinstance(condition_result, bool):
    #     raise RuntimeError(
    #         f"Expected bool from Condition result. Got {type(condition_result)}"
    #     )
    env.writeline(f'if {condition_result}:\n')
    env.scope_level += 1
    logger.debug(f'Got condition: {condition_result}')
    # if condition_result is True:
    transpile(consequent, env)
    env.scope_level -= 1
    if alternative is not None:
        env.writeline('else:\n')
        env.scope_level += 1
        transpile(alternative, env)
        env.scope_level -= 1
        env.writeline('\n')

@transpile.register(Clause)
def transpile_clause_node(clause_node, env: Environment):
    logger.debug(f"Interpreting clause node: {repr(clause_node)}")
    if hasattr(clause_node, 'is_function_clause'):
        logger.debug("Closest scope was function scope (was already created) Skipping creating child env for this clause")
        retval = None
        for statement in clause_node.statements:
            retval = transpile(statement, env)
        return retval  # Most callers won't need this, but Compound Expressions do need the last thing
    logger.debug("Closest scope was not function scope, creating new one!")
    with env.child_env():
        retval = None
        for statement in clause_node.statements:
            retval = transpile(statement, env)
        return retval  # Most callers won't need this, but Compound Expressions do need the last thing
    # env.writeline('#start clause\n')
    # for statement in clause_node.statements:
    #     logger.debug(f"Writing clause statement: {repr(statement)}")
    #     transpile(statement, env)
    # env.writeline('#end clause\n')

@transpile.register(WhileLoop)
def transpile_while_loop_node(while_loop_node: WhileLoop, env: Environment):
    cond_str = transpile(while_loop_node.condition, env)
    env.writeline(f'while {cond_str}:\n')
    env.scope_level += 1
    transpile(while_loop_node.body, env)
    env.scope_level -= 1
    env.writeline('\n')
    env.writeline('#endwhile\n')

@transpile.register(ExpressionStatement)
def transpile_expression_statement_node(expression_statement_node, env):
    return transpile(expression_statement_node.expression, env)

@transpile.register(UnaryOp)
def transpile_unary_op_node(unary_op_node, env):
    logger.debug(f'Transpiling unary opt node: {repr(unary_op_node)}')

    op = unary_op_node.op
    expr = unary_op_node.operand
    value = transpile(expr, env)
    if op == '+':
        return value
    elif op == '-':
        return f'-{value}'
    elif op == '!':
        return f' not {value}'



@transpile.register(CharacterLiteral)
def transpile_character_literal(character_literal_node, env):
    return character_literal_node.value

@transpile.register(BreakStatement)
def transpile_break_statement(_, env):
    env.writeline('break\n')

@transpile.register(ContinueStatement)
def transpile_continue_statement(_, env):
    env.writeline('continue\n')

@transpile.register(ReturnStatement)
def transpile_return_statement(return_statement_node, env):
    return_expr = return_statement_node.expression
    retval = transpile(return_expr, env)
    env.writeline(f'return {retval}')
    return #??
    # Hack to make sure illegal usage of return is not used
    # We attach the return value to the exception, so the catcher can receive the value
    logger.debug(f'raising return encountered with piggybacked value: {repr(retval)}')
    raise ReturnEncountered(
        "return statement encountered. If this bubbles up to you, it's an error due to illegal usage. "
        "Did you use continue outside a while loop?",
        retval
    )


@transpile.register(Parameter)
def transpile_param_node(param_node, env):
    return param_node  # Maybe we can just oust this altogether


# @transpile.register(FunctionDefinition)
# def transpile_function_definition_node(func_def_node: FunctionDefinition, env):
#     ...
#
#
# @transpile.register(StructDefinition)
# def transpile_struct_definition_node(struct_def_node, env):
#     raise NotImplementedError(locals())
#
#
# @transpile.register(EnumDefinition)
# def transpile_enum_definition_node(enum_def_node, env):
#     raise NotImplementedError(locals())
#
#
# @transpile.register(FunctionOrStructCall)
# def transpile_function_call_node(function_or_struct_call_node, env):
#     logger.debug("Handling struct/func call")
#     raise NotImplementedError(locals())




@transpile.register(FieldLookup)
def transpile_struct_field_lookup_node(field_lookup_node, env):
    raise NotImplementedError(locals())

# @transpile.register(EnumChoice)
# def transpile_enum_choice_node(enum_choice_node, env):
#     raise NotImplementedError(locals())

@transpile.register(EnumLookup)
def transpile_enum_lookup_node(enum_lookup_node, env):
    raise NotImplementedError(locals())



@transpile.register(CompoundExpr)
def transpile_compound_expr(compound_expr_node, env):
    raise NotImplementedError(locals())

@transpile.register(Grouping)
def transpile_grouping_node(group_node, env):
    logger.debug(f'Interpreting grouping {repr(group_node)}')
    grouping_value = transpile(group_node.expression, env)
    logger.debug(f'Group value: {grouping_value}')
    return grouping_value

@transpile.register(Unit)
def transpile_unit_node(unit_node, env):
    raise NotImplementedError(locals())


@transpile.register(Bool)
def transpile_bool_node(bool_node, env):
    return str(bool_node.value)

@transpile.register(MatchExpression)
def transpile_match_expression_node(match_expr_node, env):
    raise NotImplementedError(locals())


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    print('-' * 80)
    import sys
    from .parse import parse_file

    if len(sys.argv) != 2:
        raise SystemExit("Usage: wabbit.interp filename")
    model = parse_file(sys.argv[1])
    print(repr(model))
    print(model)
    transpile_program(model)
    print('-' * 80)

