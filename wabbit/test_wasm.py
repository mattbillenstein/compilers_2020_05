# from wabbit.wasm import *
# from wabbit.was# wasm.py

from wasmer import Instance
from wabbit.wasm import *
from wabbit.model import *


def call_statements(return_type: str, body: Statements):
    assert isinstance(body, list)
    if isinstance(body[-1], Return):
        statements = body
    else:
        statements = body + [Return()]

    model = Statements(
        [FunctionDefinition("main", [], return_type, Statements(statements))]
    )
    print(model)

    mod = generate_program(model)
    wasm_bytes = encode_module(mod.module)
    instance = Instance(wasm_bytes)

    return instance.exports.main()


def test_wasm_basic():
    result = call_statements("int", [Integer(8)])
    assert result == 8
    #
    result = call_statements("float", [Float("3.2")])
    assert result == 3.2
    #
    result = call_statements(
        "int", [Var("age", None, Integer(30)), BinOp("*", Variable("age"), Integer(2))]
    )
    assert result == 60

    #
    result = call_statements(
        "float",
        [Var("age", None, Float(30.0)), BinOp("*", Variable("age"), Float(2.5))],
    )
    assert result == 75.0


def test_functions():
    # func square(x int) int {
    #     return x*x;
    # }
    result = call_statements(
        "int",
        [
            FunctionDefinition(
                "square",
                Arguments(Argument("x", "int")),
                "int",
                Statements([Return(BinOp("*", Variable("x"), Variable("x")))]),
            ),
            FunctionCall("square", Integer(17)),
        ],
    )
    assert result == 17 * 17

    # func mul(x int, y int) int {
    #     return y*x;
    # }
    result = call_statements(
        "int",
        [
            FunctionDefinition(
                "mul",
                Arguments(Argument("x", "int"), Argument("y", "int")),
                "int",
                Statements([Return(BinOp("*", Variable("y"), Variable("x")))]),
            ),
            FunctionCall("mul", Integer(17), Integer(2)),
        ],
    )
    assert result == 17 * 2

    # func fmul(x int, y int) int {
    #     return y*x;
    # }
    result = call_statements(
        "float",
        [
            FunctionDefinition(
                "fmul",
                Arguments(Argument("x", "float"), Argument("y", "float")),
                "float",
                Statements([Return(BinOp("*", Variable("y"), Variable("x")))]),
            ),
            FunctionCall("fmul", Float("3.3"), Float("9.9")),
        ],
    )
    assert result == 3.3 * 9.9


def test_var_assignment():

    result = call_statements("int", [Var("a", "int", Integer(3)), Variable("a")])
    assert result == 3

    #     if a > 4 {
    #         return 5;
    #     } else {
    #         return 9;
    #     }
    # }
    result = call_statements(
        "int",
        [
            Var("a", "int", Integer(3)),
            If(
                BinOp(">", Variable("a"), Integer(4)),
                Statements([Return(Integer(5))]),
                Statements([Return(Integer(9))]),
            ),
            Return(Integer(0)),
        ],
    )
    assert result == 9

    #     if a > 4 {
    #         return 5;
    #     } else {
    #         return 9;
    #     }
    # }
    result = call_statements(
        "int",
        [
            Var("a", "int", Integer(6)),
            If(
                BinOp(">", Variable("a"), Integer(4)),
                Statements([Return(Integer(5))]),
                Statements([Return(Integer(9))]),
            ),
            Return(Integer(0)),
        ],
    )
    assert result == 5


def test_if_inside_func():
    # func fabs(x float) float {
    #     if x < 0.0 {
    #         return -x;
    #     } else {
    #         return x;
    #     }
    # }

    result = call_statements(
        "float",
        [
            FunctionDefinition(
                "fabs",
                Arguments(Argument("x", "float")),
                "float",
                Statements(
                    [
                        If(
                            BinOp("<", Variable("x"), Float("0.0")),
                            Statements([Return(Float("-1.0"))]),
                            Statements([Return(Float("1.0"))]),
                        ),
                        Return(Float("7.7")),
                    ]
                ),
            ),
            FunctionCall("fabs", Float("-3.2")),
        ],
    )
    assert result == -1.0
    #
    result = call_statements(
        "float",
        [
            FunctionDefinition(
                "fabs",
                Arguments(Argument("x", "float")),
                "float",
                Statements(
                    [
                        If(
                            BinOp("<", Variable("x"), Float("0.0")),
                            Statements([Return(Float("-1.0"))]),
                            Statements([Return(Float("1.0"))]),
                        ),
                        Return(Float("7.7")),
                    ]
                ),
            ),
            FunctionCall("fabs", Float("3.2")),
        ],
    )
    assert result == 1.0

    # var x = 0
    # while true {
    #     if x > 10 {
    #        break
    #     }
    #     x = x + 1
    # }


def test_while():
    result = call_statements(
        "int",
        [
            Var("x", None, Integer(0)),
            While(
                Truthy(),
                Statements(
                    [
                        If(BinOp(">", Variable("x"), Integer(10)), Break()),
                        Assignment(
                            Variable("x"), BinOp("+", Variable("x"), Integer(1))
                        ),
                    ]
                ),
            ),
            Return(Variable("x")),
        ],
    )
    assert result == 11


# def test_complex_func():

#    # func fabs(x float) float {
#    #     if x < 0.0 {
#    #         return -x;
#    #     } else {
#    #         return x;
#    #     }
#    # }

#    result = call_statements(
#        "float",
#        [
#            FunctionDefinition(
#                "fabs",
#                Arguments(Argument("x", "float")),
#                "float",
#                Statements(
#                    [
#                        If(
#                            BinOp("<", Variable("x"), Float("0.0")),
#                            Statements([Return(UnaryOp("-", Variable("x")))]),
#                            Statements([Return(Variable("x"))]),
#                        ),
#                        Return(Float("7.7")),
#                    ]
#                ),
#            ),
#            # func sqrt(x float) float {
#            #     var guess = 1.0;
#            #     var nextguess = 0.0;
#            #     if x == 0.0 {
#            #           return 0.0;
#            #     }
#            #
#            #     while true {
#            #           nextguess = (guess + (x / guess)) / 2.0;
#            # 	        if (fabs(nextguess-guess)/guess) < 0.00000001 {
#            # 	                break;
#            #           }
#            # 	   guess = nextguess;
#            #     }
#            #
#            #     return guess;
#            # }
#            FunctionDefinition(
#                "sqrt",
#                Arguments(Argument("x", "float")),
#                "float",
#                Statements(
#                    [
#                        Var("guess", None, Float("1.0")),
#                        Var("nextguess", None, Float("0.0")),
#                        If(
#                            BinOp("==", Variable("x"), Float("0.0")),
#                            Statements([Return(Float("0.0"))]),
#                        ),
#                        While(
#                            Truthy(),
#                            Statements(
#                                [
#                                    Assignment(
#                                        Variable("nextguess"),
#                                        BinOp(
#                                            "/",
#                                            BinOp(
#                                                "+",
#                                                Variable("guess"),
#                                                BinOp(
#                                                    "/",
#                                                    Variable("x"),
#                                                    Variable("guess"),
#                                                ),
#                                            ),
#                                            Float("2.0"),
#                                        ),
#                                    ),
#                                    If(
#                                        BinOp(
#                                            "<",
#                                            BinOp(
#                                                "/",
#                                                FunctionCall(
#                                                    "fabs",
#                                                    BinOp(
#                                                        "-",
#                                                        Variable("nextguess"),
#                                                        Variable("guess"),
#                                                    ),
#                                                ),
#                                                Variable("guess"),
#                                            ),
#                                            Float("0.001"),
#                                        ),
#                                        Break(),
#                                    ),
#                                    Assignment(
#                                        Variable("guess"), Variable("nextguess")
#                                    ),
#                                ]
#                            ),
#                        ),
#                        Return(Variable("guess")),
#                    ]
#                ),
#            ),
#            FunctionCall("fabs", Float("9.0")),
#        ],
#    )

#    assert result == 17 * 2


## mod = generate_program(model)
## # Write to a file
## with open("out_runtime.wasm", "wb") as file:
##     file.write(encode_module(mod))
## assert encode_module(mod) == ""

