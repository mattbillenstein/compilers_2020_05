def tokenize(text: str):
    for tok in text.split():
        if tok in ["+", "-", "*", "/"]:
            yield "OP", tok
        elif tok in ["="]:
            yield "ASSIGN", tok
        elif _is_numeric(tok):
            yield "NUM", tok
        else:
            yield "NAME", tok


def _is_numeric(token):
    if token.isdecimal():
        return True
    try:
        float(token)
    except ValueError:
        return False
    else:
        return True


assert list(tokenize("spam = x + 34 * 567")) == [
    ("NAME", "spam"),
    ("ASSIGN", "="),
    ("NAME", "x"),
    ("OP", "+"),
    ("NUM", "34"),
    ("OP", "*"),
    ("NUM", "567"),
]
