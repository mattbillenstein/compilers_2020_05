def convert_numbers(tree):
    if not isinstance(tree, tuple):
        try:
            return int(tree)
        except (TypeError, ValueError):
            return tree
    else:
        return tuple(convert_numbers(el) for el in tree)


tree = (
    "assign",
    "spam",
    ("binop", "+", ("name", "x"), ("binop", "*", ("num", "34"), ("num", "567"))),
)

assert convert_numbers(tree) == (
    "assign",
    "spam",
    ("binop", "+", ("name", "x"), ("binop", "*", ("num", 34), ("num", 567))),
)
