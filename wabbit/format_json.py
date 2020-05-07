import json

from typeguard import typechecked

from wabbit.model import Node


class NodeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Node):
            return repr(obj)


class TreeFormatter:
    """
    Format model as JSON-encodable tree.
    """

    @typechecked
    def visit(self, node: Node, **kwargs):
        data = node.__dict__.copy()
        for child in ["left", "right", "then", "test", "else_"]:
            if hasattr(node, child):
                data[child] = self.visit(getattr(node, child))
        if hasattr(node, "statements"):
            data["statements"] = [self.visit(s) for s in node.statements]  # type: ignore
        data["type"] = node.__class__.__name__
        return data


def format_json(node):
    return json.dumps(TreeFormatter().visit(node), indent=2, cls=NodeJSONEncoder)
