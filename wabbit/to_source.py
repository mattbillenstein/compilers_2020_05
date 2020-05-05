from functools import singledispatch
from .model import *


@singledispatch
def to_source(node):
    raise RuntimeError(f"Can't convert {node} to source")


rule = to_source.register


@rule(BinOp)
def to_source_BinOp(node):
    return f"{to_source(node.left)} {node.op} {to_source(node.right)}"


@rule(Integer)
def to_source_Integer(node):
    return repr(node.value)


@rule(EnumChoice)
def to_source_EnumChoice(node):
    if node.type:
        return f"{node.name}({node.type})"
    return f"{node.name}"


@rule(Enum)
def to_source_Enum(node):
    args = ";\n".join([to_source(c) for c in node.choices])
    return f"enum {node.name} {{\n{args};\n}}"


@rule(EnumLocation)
def to_source_EnumLocation(node):
    if node.args:
        return f"{node.enum}::{node.location}({to_source(node.args)})"
    return f"{node.enum}::{node.location}"


@rule(MatchCondition)
def to_source_MatchCondition(node):
    return f"{to_source(node.choice)} => {to_source(node.expression)}"


@rule(Match)
def to_source_Match(node):
    args = ";\n".join([to_source(c) for c in node.conditions])
    return f"match({node.test}) {{\n {args}; \n}}"


@rule(Struct)
def to_source_Struct(node):
    args = "\n".join([to_source(s) for s in node.args])
    return f"struct {node.name} {{\n {args} \n }}"


@rule(Argument)
def to_source_Argument(node):
    return f"{node.name} {node.type}"


@rule(Arguments)
def to_source_Arguments(node):
    return ", ".join([to_source(s) for s in node.args])


@rule(FunctionCall)
def to_source_FunctionCall(node):
    args = ", ".join([to_source(s) for s in node.args])
    return f"{node.name}({args})"


@rule(FunctionDefinition)
def to_source_FunctionDefinition(node):
    if node.return_type:
        return_type = to_source(node.return_type)
    else:
        return_type = f""

    if node.body:
        body = to_source(node.body)
    else:
        body = f""

    if node.args:
        args = to_source(node.args)

    else:
        args = f""
    return f"func {node.name}({args}) {return_type} {{ \n {body}\n}}"


@rule(Block)
def to_source_Block(node):
    joined_statements = "; ".join([to_source(s) for s in node.statements])
    return f"{{ {joined_statements} }};"


@rule(Statements)
def to_source_Statements(node):
    return "\n".join([to_source(s) for s in node.statements])


@rule(If)
def to_source_If(node):
    return f"if {to_source(node.test)} {{\n   {to_source(node.when_true)}\n}} else {{\n   {to_source(node.when_false)}\n}}"


@rule(While)
def to_source_While(node):
    return f"while {to_source(node.test)} {{\n   {to_source(node.when_true)}\n}}"


@rule(Assignment)
def to_source_Assignment(node):
    return f"{to_source(node.location)} = {to_source(node.expression)}"


@rule(Return)
def to_source_Return(node):
    return f"return {to_source(node.value)}"


@rule(Print)
def to_source_Print(node):
    return f"print {to_source(node.value)}"


@rule(Float)
def to_source_Float(node):
    return repr(node.value)


@rule(Const)
def to_source_Const(node):
    if node.type:
        return f"const {node.name} {node.type} = {to_source(node.value)}"
    return f"const {node.name} = {to_source(node.value)}"


@rule(Var)
def to_source_Var(node):
    base = f"var {node.name}"
    if node.type:
        base += f" {node.type}"
    if node.value:
        base += f" = {to_source(node.value)}"
    return base


@rule(Let)
def to_source_Let(node):
    return f"let {node.name} = {to_source(node.value)}"


@rule(Variable)
def to_source_Variable(node):
    return node.name


@rule(UnaryOp)
def to_source_UnaryOp(node):
    return f"{node.op}{to_source(node.target)}"
