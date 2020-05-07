


_bin_ops = {
    # Integer operations
    ('+', 'int', 'int') : 'int',
    ('-', 'int', 'int') : 'int',
    ('*', 'int', 'int') : 'int',
    ('/', 'int', 'int') : 'int',
    ('<', 'int', 'int') : 'bool',
    ('<=', 'int', 'int') : 'bool',
    ('>', 'int', 'int') : 'bool',
    ('>=', 'int', 'int') : 'bool',
    ('==', 'int', 'int') : 'bool',
    ('!=', 'int', 'int') : 'bool',

    # Float operations
    ('+', 'float', 'float') : 'float',
    ('-', 'float', 'float') : 'float',
    ('*', 'float', 'float') : 'float',
    ('/', 'float', 'float') : 'float',
    ('<', 'float', 'float') : 'bool',
    ('<=', 'float', 'float') : 'bool',
    ('>', 'float', 'float') : 'bool',
    ('>=', 'float', 'float') : 'bool',
    ('==', 'float', 'float') : 'bool',
    ('!=', 'float', 'float') : 'bool',

    # Char operations
    ('<', 'char', 'char') : 'bool',
    ('<=', 'char', 'char') : 'bool',
    ('>', 'char', 'char') : 'bool',
    ('>=', 'char', 'char') : 'bool',
    ('==', 'char', 'char') : 'bool',
    ('!=', 'char', 'char') : 'bool',

    # Bool operations
    ('==', 'bool', 'bool') : 'bool',
    ('!=', 'bool', 'bool') : 'bool',
    ('&&', 'bool', 'bool') : 'bool',
    ('||', 'bool', 'bool') : 'bool',
}

_unary_ops = {
    ('+', 'int') : 'int',
    ('-', 'int') : 'int',
    ('+', 'float') : 'float',
    ('-', 'float') : 'float',
    ('!', 'bool') : 'bool',
    }

