
from wabbit.tokenize import tokenize

def test_operators():
    tok_types = [t.type for t in list(tokenize('+ - * / < <= > >= == !='))]
    assert(tok_types == ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NE'])

def test_keywords():
    kws = ' '.join([ 'const', 'var', 'print', 'break', 'continue', 'if', 'else', 'while', 'true', 'false', ])
    tok_types = [t.type for t in list(tokenize(kws))]
    assert(tok_types == ['CONST', 'VAR', 'PRINT', 'BREAK', 'CONTINUE', 'IF', 'ELSE', 'WHILE', 'TRUE', 'FALSE'])

def test_int():
    s = '1 23 456789'
    tok_types = [t.type for t in list(tokenize(s))]
    assert(tok_types == ['NUMBER', 'NUMBER', 'NUMBER'])

def test_float():
    s = '1.234 .1234  1234.'
    tok_types = [t.type for t in list(tokenize(s))]
    assert(tok_types == ['DECIMAL', 'DECIMAL', 'DECIMAL'])

def test_vars():
    s = 'printable holy_moly scontinue ifelsewhile'
    tok_types = [t.type for t in list(tokenize(s))]
    assert(tok_types == ['VAR_NAME', 'VAR_NAME', 'VAR_NAME', 'VAR_NAME'])

def test_ops():
    s = '+ - * / < <= > >= == != && || !'
    tok_types = [t.type for t in list(tokenize(s))]
    assert(tok_types == ['PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LT', 'LE', 'GT', 'GE', 'EQ', 'NE', 'LAND', 'LOR', 'LNOT'])

def test_char():
    s = "'a'  'b' 'c'"
    tok_types = [t.type for t in list(tokenize(s))]
    assert(tok_types == ['CHAR', 'CHAR', 'CHAR'])

def test_comments():
    s = """
      yeehaw // comment
      /* no
      no
      no
      */
      yipee
      """
    tok_values = [t.value for t in list(tokenize(s))]
    print(tok_values)
    assert(tok_values == ['yeehaw', 'yipee'])

def test_dot():
    s = "a.x.y = 3"
    tok_types = [t.type for t in list(tokenize(s))]
    assert(tok_types == ['VAR_NAME', 'DOT', 'VAR_NAME', 'DOT', 'VAR_NAME', 'ASSIGN', 'NUMBER'])
