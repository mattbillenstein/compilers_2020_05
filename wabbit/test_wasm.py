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

    #     # result = instance.exports.main()
    #     # assert result == 2.2

    #     # model = Statements([Var("naz", "char", Char("N")), Variable("naz")])

    #     # mod = generate_program(model)

    #     # wasm_bytes = encode_module(mod.module)
    #     # instance = Instance(wasm_bytes)

    #     # result = instance.exports.main()
    #     # assert result == 78

    #     # model = Statements([Integer(5)])

    #     # mod = generate_program(model)

    #     # wasm_bytes = encode_module(mod.module)
    #     # instance = Instance(wasm_bytes)

    #     # result = instance.exports.main()
    #     # assert result == 7

    #     model = Statements(
    #         [Var("age", None, Integer(30)), BinOp("*", Variable("age"), Integer(2))]
    #     )

    #     mod = generate_program(model)

    #     wasm_bytes = encode_module(mod.module)
    #     instance = Instance(wasm_bytes)

    #     result = instance.exports.main()
    #     assert result == 60

    #     # func square(x int) int {
    #     #     return x*x;
    #     # }
    #     model = Statements(
    #         [
    #             FunctionDefinition(
    #                 "square",
    #                 Arguments(Argument("x", "int")),
    #                 "int",
    #                 Statements([BinOp("*", Variable("x"), Variable("x"))]),
    #             ),
    #             FunctionCall("square", Integer(17)),
    #         ]
    #     )

    #     mod = generate_program(model)

    #     wasm_bytes = encode_module(mod.module)
    #     instance = Instance(wasm_bytes)

    #     result = instance.exports.main()
    #     assert result == 17 * 17

    #     # func mul(x int, y int) int {
    #     #     return y*x;
    #     # }
    #     model = Statements(
    #         [
    #             FunctionDefinition(
    #                 "mul",
    #                 Arguments(Argument("x", "int"), Argument("y", "int")),
    #                 "int",
    #                 Statements([BinOp("*", Variable("y"), Variable("x"))]),
    #             ),
    #             FunctionCall("mul", Integer(17), Integer(2)),
    #         ]
    #     )

    #     mod = generate_program(model)

    #     wasm_bytes = encode_module(mod.module)
    #     instance = Instance(wasm_bytes)

    #     result = instance.exports.main()
    #     assert result == 17 * 2

    #     #     if 2 > 4 {
    #     #         return 1;
    #     #     } else {
    #     #         return 2;
    #     #     }
    #     # }

    #     model = Statements(
    #         [
    #             If(
    #                 BinOp(">", Integer(2), Integer(4)),
    #                 Statements([Return(Integer(1))]),
    #                 Statements([Return(Integer(2))]),
    #             )
    #         ]
    #     )

    #     mod = generate_program(model)

    #     wasm_bytes = encode_module(mod.module)
    #     instance = Instance(wasm_bytes)

    #     result = instance.exports.main()
    #     assert result == 2

    # func fabs(x float) float {
    #     if x < 0.0 {
    #         return -x;
    #     } else {
    #         return x;
    #     }
    # }

    model = Statements(
        [
            FunctionDefinition(
                "fabs",
                Arguments(Argument("x", "int")),
                "int",
                Statements(
                    [
                        If(
                            BinOp("<", Variable("x"), Integer(1)),
                            Statements([Return(Integer(1))]),
                        ),
                        Return(Variable("x")),
                    ]
                ),
            ),
            FunctionCall("fabs", Integer(3)),
        ]
    )

    mod = generate_program(model)

    wasm_bytes = encode_module(mod.module)
    instance = Instance(wasm_bytes)

    result = instance.exports.main()
    assert result == 17 * 2


#     # func sqrt(x float) float {
#     #     var guess = 1.0;
#     #     var nextguess = 0.0;
#     #     if x == 0.0 {
#     #         return 0.0;
#     #     }
#     #     while true {
#     #         nextguess = (guess + (x / guess)) / 2.0;
#     # 	if (fabs(nextguess-guess)/guess) < 0.00000001 {
#     # 	    break;
#     #         }
#     # 	guess = nextguess;
#     #     }
#     #     return guess;
#     # }
#     model = Statements(
#         [
#             If(
#                 BinOp(">", Integer(2), Integer(4)),
#                 Statements([Integer(1)]),
#                 Statements([Integer(2)]),
#             )
#         ]
#     )

#     mod = generate_program(model)

#     wasm_bytes = encode_module(mod.module)
#     instance = Instance(wasm_bytes)

#     result = instance.exports.main()
#     assert result == 17 * 2

# mod = generate_program(model)
# # Write to a file
# with open("out_runtime.wasm", "wb") as file:
#     file.write(encode_module(mod))
# assert encode_module(mod) == ""

