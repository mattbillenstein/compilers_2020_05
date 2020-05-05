import json

from difflib import unified_diff
from subprocess import Popen, PIPE


def bat(source, language="go"):
    """
    https://github.com/sharkdp/bat/
    """
    proc = Popen(["bat", "--language", language], stdin=PIPE)
    proc.stdin.write(source.encode("utf-8"))  # type: ignore
    proc.communicate()


def delta(a, b):
    """
    https://github.com/dandavison/delta
    """
    if not (isinstance(a, str) and isinstance(b, str)):
        a = to_json(a)
        b = to_json(b)
    diff = "\n".join(unified_diff(a.splitlines(), b.splitlines()))
    proc = Popen(["delta"], stdin=PIPE)
    proc.stdin.write(diff.encode("utf-8"))  # type: ignore
    proc.communicate()


def to_json(obj):
    return json.dumps(obj, sort_keys=True, indent=2)
