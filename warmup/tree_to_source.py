def to_source(tree):
    """
    The current node may be:

    - binop       - binary, infix formatting, arg1 and arg2 are nodes
    - assign      - binary, infix formatting, arg1 is a string and arg2 is a node
    - {name, num} - unary, arg is a string
    """
    tok_type, *args = tree

    if tok_type == "binop":
        (tok, arg1, arg2) = args
        return " ".join([to_source(arg1), tok, to_source(arg2)])
    elif tok_type == "assign":
        tok = "="
        (lvalue, rvalue) = args
        return " ".join([lvalue, tok, to_source(rvalue)])
    else:
        (value,) = args
        return value


tree = (
    "assign",
    "spam",
    ("binop", "+", ("name", "x"), ("binop", "*", ("num", "34"), ("num", "567"))),
)

assert to_source(tree) == "spam = x + 34 * 567"
