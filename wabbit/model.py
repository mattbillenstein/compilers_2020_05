class Integer:
    """
    Example: 42
    """

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Integer({self.value})"


class BinOp:
    """
    Example: left + right
    """

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinOp({self.op}, {self.left}, {self.right})"


def to_source(node):
    if isinstance(node, Integer):
        return repr(node.value)
    elif isinstance(node, BinOp):
        return f"{to_source(node.left)} {node.op} {to_source(node.right)}"
    else:
        raise RuntimeError(f"Can't convert {node} to source")
