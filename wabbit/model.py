from dataclasses import dataclass
from typing import Any, Union, Optional, List


class Node():
    def __repr__(self):
        return "{}.{}<{}>({})".format(self.__class__.__module__, self.__class__.__name__, id(self), self.__dict__)

    def visit(self, visitor):
        methname = 'visit_' + type(self).__name__
        meth = getattr(visitor, methname, None)
        if meth is None:
            raise NotImplementedError
        return meth(self)


class ExpressionNode(Node):
    pass


class StatementNode(Node):
    pass


class BlockNode(Node):
    lines: List[StatementNode]


class ScalarNode(ExpressionNode):
    def visit(self, visitor):
        return visitor.visit_ScalarNode(self)


@dataclass
class StorageIdentifier(ScalarNode):
    value: str


@dataclass
class Int(ScalarNode):
    value: int


@dataclass
class Float(ScalarNode):
    value: float


@dataclass
class StorageLocation(ExpressionNode):
    identifier: StorageIdentifier


@dataclass
class DeclStorageLocation(StorageLocation):
    identifier: StorageIdentifier
    _type: str = None
    const: bool = False


@dataclass
class AssignStatement(StatementNode):
    location: StorageLocation
    value: ExpressionNode


@dataclass
class BinOp(ExpressionNode):
    op: str
    left: ExpressionNode
    right: ExpressionNode


@dataclass
class UnOp(ExpressionNode):
    op: str
    right: ExpressionNode


@dataclass
class PrintStatement(StatementNode):
    expr: ExpressionNode


@dataclass
class ConditionalStatement(StatementNode):
    cond: ExpressionNode
    blockT: List[StatementNode]
    blockF: List[StatementNode]


@dataclass
class ConditionalLoopStatement(StatementNode):
    cond: ExpressionNode
    block: List[StatementNode]


@dataclass
class BlockExpression(ExpressionNode):
    block: List[StatementNode]


@dataclass
class ExpressionStatement(StatementNode):
    statement: ExpressionNode


@dataclass
class FuncCall(ExpressionNode):
    name: str
    args: List[ExpressionNode]


@dataclass
class FuncDeclStatement(StatementNode):
    name: str
    args: List[List[str]]
    retval: str
    body: List[StatementNode]


@dataclass
class ReturnStatement(StatementNode):
    retval: ExpressionNode


class ModelVisitor:
    def __init__(self):
        raise NotImplementedError

    def visit_StorageLocation(self, node):
        raise NotImplementedError

    def visit_DeclStorageLocation(self, node):
        raise NotImplementedError

    def visit_ScalarNode(self, node):
        raise NotImplementedError

    def visit_AssignStatement(self, node):
        raise NotImplementedError

    def visit_BinOp(self, node):
        raise NotImplementedError

    def visit_UnOp(self, node):
        raise NotImplementedError

    def visit_PrintStatement(self, node):
        raise NotImplementedError

    def visit_ConditionalStatement(self, node):
        raise NotImplementedError

    def visit_ConditionalLoopStatement(self, node):
        raise NotImplementedError

    def visit_BlockExpression(self, node):
        raise NotImplementedError

    def visit_ExpressionStatement(self, node):
        raise NotImplementedError

    def visit_FuncCall(self, node):
        raise NotImplementedError

    def visit_FuncDeclStatement(self, node):
        raise NotImplementedError

    def visit_ReturnStatement(self, node):
        raise NotImplementedError
