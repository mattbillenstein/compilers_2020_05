# testlex.py
#
# Example of unit tests on tokens.  Assumes "pytest" for testing

from wabbit.tokenize import tokenize

def test_operators():
    toks = list(tokenize("+ - * / < <= > >= == != && || !"))
    tok_types = [tok.type for tok in toks]
    assert tok_types == ['PLUS', 'MINUS', 'TIMES', 'DIVIDE',
                         'LT', 'LE', 'GT', 'GE', 'EQ', 'NE', 'LAND', 'LOR', 'LNOT']

def test_keywords():
    toks = list(tokenize("var const if print while else break continue true false"))
    tok_types = [tok.type for tok in toks]
    assert tok_types == ['VAR', 'CONST', 'IF', 'PRINT', 'WHILE',
                        'ELSE', 'BREAK', 'CONTINUE', 'TRUE', 'FALSE']

def test_numbers():
    toks = list(tokenize("123 12.3 123. .123"))
    tok_types = [tok.type for tok in toks]
    assert tok_types == ['INTEGER', 'FLOAT', 'FLOAT', 'FLOAT']

def test_block_comment1():
    toks = list(tokenize("/* comment1 */ 123 /* comment 2 */"))
    assert len(toks) == 1 and toks[0].type == 'INTEGER'

def test_char_const():
    toks = list(tokenize("'x' 'y' '\\n' '\\''"))
    tok_types = [tok.type for tok in toks]
    assert all(ty == 'CHAR' for ty in tok_types)

