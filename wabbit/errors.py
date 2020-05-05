class RootException(Exception):
    """
    Top-level exception everything inherits from
    """

    pass


class InterpreterException(RootException):
    """
    Generic errors thrown from inside the Interpreter
    """

    pass
