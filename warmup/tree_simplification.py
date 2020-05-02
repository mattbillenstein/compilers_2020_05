import operator

OPERATORS = {
    "+": operator.add,
    "*": operator.mul,
    "/": operator.truediv,
}


def simplify_tree(tree):
    """
    If we are at an internal node, process children, and then try to simplify.
    """
    if not isinstance(tree, tuple):
        return tree
    else:
        tree = tuple(simplify_tree(el) for el in tree)
        if tree[0] == "binop":
            return _simplify_binop_expression(*tree[1:]) or tree
        else:
            return tree


def _simplify_binop_expression(op_token, arg1, arg2):
    if arg1[0] == "num" and arg2[0] == "num":
        return ("num", OPERATORS[op_token](arg1[1], arg2[1]))


tree = ("assign", "spam", ("binop", "+", ("name", "x"), ("binop", "*", ("num", 34), ("num", 567))))

assert simplify_tree(tree) == (
    "assign",
    "spam",
    ("binop", "+", ("name", "x"), ("num", 19278)),
), simplify_tree(tree)
