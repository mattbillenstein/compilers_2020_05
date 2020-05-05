from wabbit.model import *
from wabbit.interp import interpret, interpret_program

print(-2)
node = BinOp('+', Integer(1), Integer(1))
print(interpret(node, {}), 'should be 2')
print()

print(-1)
node = BinOp('*', Integer(100), Integer(3))
print(interpret(node, {}), 'should be 300')
print()


print(1)
model1 = Statements([
    PrintStatement(BinOp('+', Integer(2), BinOp('*', Integer(3), Integer(-4)))),
    PrintStatement(BinOp('-', Float(2.0), BinOp('/', Float(3.0), Float(-4.0)))),
    PrintStatement(BinOp('+', Integer(-2), Integer(3))),
    PrintStatement(BinOp('*', Integer(2), BinOp('+', Integer(3), Integer(-4)))),
])
interpret(model1, {})
print()


print('2 part 0')
env = {}
print('a', interpret(Const('pi', Float(3.14159)), env))
print('env after', env)
env = {}
print('b', interpret(Var('tau', 'float'), env))
print('env after', env)
env = {}
print('c', interpret(Statements([Var('tau', 'float'), Assign(Variable('tau'), Float(0.6))]), env))
print('env after', env)
print()



print(2)
model2 = Statements([
    Const('pi', Float(3.14159)),
    Var('tau', 'float'),
    Assign(Variable('tau'), BinOp('*', Float(2.0), Variable('pi'))),
    PrintStatement(Variable('tau')),
])
interpret(model2, {})
print()



print(3)
model3 = Statements([
    Assign(Var('a', 'int'), Integer(2)),
    Assign(Var('b', 'int'), Integer(3)),
    IfElse(BinOp('<', Variable('a') , Variable('b')), Statements([PrintStatement(Variable('a')),]), Statements([PrintStatement(Variable('b')),])),
])
env = {}
interpret(model3, env)
print('env after', env)
print()


source4 = '''
    const n = 10;
    var x int = 1;
    var fact int = 1;

    while x < n {
        fact = fact * x;
        print fact;
        x = x + 1;
    }
'''

model4 = Statements([
    Const('n', Integer(10)),
    Assign(Var('x', 'int'), Integer(1)),
    Assign(Var('fact', 'int'), Integer(1)),
    While(BinOp('<', Variable('x'), Variable('n')), Statements([
        Assign(Variable('fact'), BinOp('*', Variable('fact'), Variable('x'))),
        PrintStatement(Variable('x')),
        Assign(Variable('x'), BinOp('+', Variable('x'), Integer(1))),
        ])),
    ])
print(4)
env = {}
interpret(model4, env)
print('env after', env)
print()
