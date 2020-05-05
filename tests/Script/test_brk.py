from wabbit.tokenize import tokenize


def test_chartest():
    with open("tests/Script/brk.wb") as file:
        text = file.read()

    result = tokenize(text)

    data = next(result)
    assert data.type == "VAR"

    data = next(result)
    assert data.type == "NAME"
    assert data.value == "n"

    data = next(result)
    assert data.type == "NAME"
    assert data.value == "int"

    data = next(result)
    assert data.type == "ASSIGN"

    data = next(result)
    assert data.type == "INTEGER"
    assert data.value == 0

    data = next(result)
    assert data.type == "SEMI"

    data = next(result)
    assert data.type == "WHILE"

    data = next(result)
    assert data.type == "TRUE"

    data = next(result)
    assert data.type == "LBRACE"

    data = next(result)
    assert data.type == "NAME"
    assert data.value == "n"

    data = next(result)
    assert data.type == "ASSIGN"

    data = next(result)
    assert data.type == "NAME"
    assert data.value == "n"

    data = next(result)
    assert data.type == "PLUS"

    data = next(result)
    assert data.type == "INTEGER"
    assert data.value == 1

    data = next(result)
    assert data.type == "SEMI"

    data = next(result)
    assert data.type == "IF"

    data = next(result)
    assert data.type == "NAME"
    assert data.value == "n"

    data = next(result)
    assert data.type == "EQ"

    data = next(result)
    assert data.type == "INTEGER"
    assert data.value == 5

    data = next(result)
    assert data.type == "LBRACE"

    data = next(result)
    assert data.type == "CONTINUE"

    data = next(result)
    assert data.type == "SEMI"

    data = next(result)
    assert data.type == "RBRACE"

    data = next(result)
    assert data.type == "PRINT"

    data = next(result)
    assert data.type == "NAME"
    assert data.value == "n"

    data = next(result)
    assert data.type == "SEMI"

    data = next(result)
    assert data.type == "IF"

    data = next(result)
    assert data.type == "NAME"
    assert data.value == "n"

    data = next(result)
    assert data.type == "GT"

    data = next(result)
    assert data.type == "INTEGER"
    assert data.value == 10

    data = next(result)
    assert data.type == "LBRACE"

    data = next(result)
    assert data.type == "BREAK"

    data = next(result)
    assert data.type == "SEMI"

    data = next(result)
    assert data.type == "RBRACE"

    data = next(result)
    assert data.type == "RBRACE"

    data = next(result)
    assert data.type == "PRINT"

    data = next(result)
    assert data.type == "MINUS"

    data = next(result)
    assert data.type == "INTEGER"
    assert data.value == 1
