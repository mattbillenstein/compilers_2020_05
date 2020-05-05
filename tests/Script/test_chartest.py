from wabbit.tokenize import tokenize


def test_chartest():
    with open("tests/Script/chartest.wb") as file:
        text = file.read()

    result = tokenize(text)

    data = next(result)
    assert data.type == "CONST"

    data = next(result)
    assert data.type == "NAME"
    assert data.value == "newline"

    data = next(result)
    assert data.type == "ASSIGN"

    data = next(result)
    assert data.type == "CHAR"
    assert data.value == "\\n"

    data = next(result)
    assert data.type == "SEMI"

    for expected in ["h", "e", "l", "l", "o"]:
        data = next(result)
        assert data.type == "PRINT"

        data = next(result)
        assert data.type == "CHAR"
        assert data.value == expected

        data = next(result)
        assert data.type == "SEMI"

    data = next(result)
    assert data.type == "PRINT"

    data = next(result)
    assert data.type == "NAME"
    assert data.value == "newline"

    data = next(result)
    assert data.type == "SEMI"

    for expected in ["w", "o", "r", "l", "d"]:
        data = next(result)
        assert data.type == "PRINT"

        data = next(result)
        assert data.type == "CHAR"
        assert data.value == expected

        data = next(result)
        assert data.type == "SEMI"

    data = next(result)
    assert data.type == "PRINT"

    data = next(result)
    assert data.type == "NAME"
    assert data.value == "newline"

    data = next(result)
    assert data.type == "SEMI"
