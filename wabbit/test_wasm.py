# from wabbit.wasm import *
# from wabbit.was# wasm.py

from wasmer import Instance
from wabbit.wasm import *
from wabbit.model import *

# def test_wasm():
# mod = WasmModule("example")
# _print = WasmImportedFunction(mod, "runtime", "_print", [INT32], [])
# main = WasmFunction(mod, "main", [], [])
# main.iconst(42)
# main.call(_print)
# main.iconst(2)
# main.iconst(3)
# main.imul()
# main.iconst(4)
# main.iconst(5)
# main.imul()
# main.iadd()
# main.call(_print)
# main.ret()

# # Write to a file
# with open("out_runtime.wasm", "wb") as file:
#     file.write(encode_module(mod))


def test_wasm_basic():
    # model = Statements([BinOp("*", Float("9.3"), Float("2.3"))])

    # mod = generate_program(model)
    # # Write to a file
    # with open("out_runtime.wasm", "wb") as file:
    #     file.write(encode_module(mod))
    # assert encode_module(mod) == ""

    # model = Statements([Float("2.2")])

    # mod = generate_program(model)

    # wasm_bytes = encode_module(mod.module)
    # instance = Instance(wasm_bytes)

    # result = instance.exports.main()
    # assert result == 2.2

    # model = Statements([Var("naz", "char", Char("N")), Variable("naz")])

    # mod = generate_program(model)

    # wasm_bytes = encode_module(mod.module)
    # instance = Instance(wasm_bytes)

    # result = instance.exports.main()
    # assert result == 78

    # model = Statements([Integer(5)])

    # mod = generate_program(model)

    # wasm_bytes = encode_module(mod.module)
    # instance = Instance(wasm_bytes)

    # result = instance.exports.main()
    # assert result == 7

    model = Statements(
        [Var("age", None, Integer(30)), BinOp("*", Variable("age"), Integer(2))]
    )

    mod = generate_program(model)

    wasm_bytes = encode_module(mod.module)
    instance = Instance(wasm_bytes)

    result = instance.exports.main()
    assert result == 60

    # func square(x int) int {
    #     return x*x;
    # }
    model = Statements(
        [
            FunctionDefinition(
                "square",
                Arguments(Argument("x", "int")),
                "int",
                Statements([Return(Integer(5))]),
                # Statements([BinOp("*", Variable("x"), Variable("x"))]),
            ),
            FunctionCall("square", Integer(2)),
        ]
    )

    mod = generate_program(model)

    wasm_bytes = encode_module(mod.module)
    instance = Instance(wasm_bytes)

    result = instance.exports.main()
    assert result == 60

    # model = Statements(
    #     [
    #         If(
    #             BinOp(">", Integer(5), Integer(4)),
    #             Statements([Print(Integer(3))]),
    #             Statements([Print(Integer(2))]),
    #         )
    #     ]
    # )

    # mod = generate_program(model)
    # # Write to a file
    # with open("out_runtime.wasm", "wb") as file:
    #     file.write(encode_module(mod))
    # assert encode_module(mod) == ""
