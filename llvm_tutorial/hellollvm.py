# hellollvm.py
from llvmlite import ir

mod = ir.Module('hello')
int_type = ir.IntType(32)

hello_func = ir.Function(mod, ir.FunctionType(int_type, []), name='hello')
block = hello_func.append_basic_block('entry')
builder = ir.IRBuilder(block)

x = builder.alloca(int_type, name='x')
y = builder.alloca(int_type, name='y')
builder.store(ir.Constant(int_type, 4), x)
builder.store(ir.Constant(int_type, 5), y)
r1 = builder.load(x)
r2 = builder.mul(r1, r1)
r3 = builder.load(y)
r4 = builder.mul(r3, r3)
r5 = builder.add(r2, r4)
d = builder.alloca(int_type, name='d')
builder.store(r5, d)
builder.ret(builder.load(d))

print(mod)
