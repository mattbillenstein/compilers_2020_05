# parse.py
#
# Wabbit parser.  The parser needs to construct the data model or an
# abstract syntax tree from text input.  The grammar shown here represents
# WabbitScript--a subset of the full Wabbit language.  It's written as
# a EBNF.  You will need to expand the grammar to include later features.
#
# Reference: https://github.com/dabeaz/compilers_2020_05/wiki/WabbitScript
#

# How to proceed:
#
# At first glance, writing a parser might look daunting. The key is to
# take it in tiny pieces.  Focus on one specific part of the language.
# For example, the print statement.  Start with something really basic
# like printing literals:
#
#     print 1;
#     print 2.5;
#
# From there, expand it to handle expressions:
#
#     print 2 + 3 * -4;
#
# Then, expand it to include variable names
#
#     var x = 3;
#     print 2 + x;
#
# Keep on expanding to more and more features of the language.  A good
# trajectory is to follow the programs found in the top level
# script_models.py file.  That is, write a parser that can recognize the
# source code for each part and build the corresponding model.  You
# will find yourself filling in pieces here throughout the project.
# It's ok to work piecemeal.
#
# Usage of tools:
#
# If you are highly motivated and want to know how a parser works at a
# low-level, you can write a hand-written recursive descent parser.
# It is also fine to use high-level tools such as
#
#    - SLY (https://github.com/dabeaz/sly),
#    - PLY (https://github.com/dabeaz/ply),
#    - ANTLR (https://www.antlr.org).

from sly import Parser
from .model import *
from .tokenize import tokenize, WabbitLexer


class WabbitParser(Parser):
    tokens = WabbitLexer.tokens

    debugfile = "parser.out"

    precedence = (("left", PLUS), ("left", MINUS), ("left", DIVIDE), ("left", TIMES))

    # program : statements EOF
    @_("statements")
    def program(self, p):
        return p.statements

    # statements : { statement }
    @_("{ statement }")
    def statements(self, p):
        return Statements(p.statement)

    # statement : print_statement
    #           | assignment_statement
    #           | variable_definition
    #           | const_definition
    #           | func_definition
    #           | struct_definition
    #           | enum_definition
    #           | if_statement
    #           | if_let_statement
    #           | while_statement
    #           | while_let_statement
    #           | break_statement
    #           | continue_statement
    #           | return_statement
    #           | expression SEMI
    @_(
        "print_statement",
        # "assignment_statement",
        # "variable_definition",
        # "const_definition",
        # "func_definition",
        # "struct_definition",
        # "enum_definition",
        # "if_statement",
        # "if_let_statement",
        # "while_statement",
        # "while_let_statement",
        # "break_statement",
        # "continue_statement",
        # "return_statement",
    )
    def statement(self, p):
        return p[0]

    @_("expression SEMI",)
    def statement(self, p):
        return p.expression

    # print_statement : PRINT expression SEMI
    @_("PRINT expression SEMI")
    def print_statement(self, p):
        return Print(p.expression)

    # assignment_statement : location ASSIGN expression SEMI
    @_("location ASSIGN expression SEMI")
    def assignment_statement(self, p):
        return Assignment(location, expression)

    # variable_definition : VAR NAME [ NAME ] ASSIGN expression SEMI
    #                     | VAR NAME NAME [ ASSIGN expression ] SEMI
    @_(
        "VAR NAME [ NAME ] ASSIGN expression SEMI",
        "VAR NAME NAME [ ASSIGN expression ] SEMI",
    )
    def variable_definition(self, p):
        return Var(p.NAME0, p.NAME1, expression)

    # const_definition : CONST NAME [ NAME ] ASSIGN expression SEMI
    @_("CONST NAME [ NAME ] ASSIGN expression SEMI")
    def const_definition(self, p):
        return Const(p.NAME0, p.NAME1, expression)

    # func_definition : FUNC NAME LPAREN [ parameters ] RPAREN NAME LBRACE statements RBRACE
    @_("FUNC NAME LPAREN [ parameters ] RPAREN NAME LBRACE statements RBRACE")
    def func_definition(self, p):
        return FunctionDefinition(p.NAME0, parameters, p.NAME1, statements)

    # parameters : parameter { COMMA parameter }
    #            | empty
    @_("parameter { COMMA parameter }", "empty")
    def parameters(self, p):
        if p.empty:
            return p.empty
        return Arguments(*p.parameter)

    # parameter  : NAME NAME
    @_("NAME NAME")
    def parameter(self, p):
        return Argument(p.NAME0, p.NAME1)

    # struct_definition : STRUCT NAME LBRACE { struct_field } RBRACE
    @_("STRUCT NAME LBRACE { struct_field } RBRACE")
    def struct_definition(self, p):
        return Struct(p.NAME, *p.struct_field)

    # struct_field : NAME NAME SEMI
    @_("NAME NAME SEMI")
    def struct_field(self, p):
        return Argument(p.NAME0, p.NAME1)

    # enum_definition : ENUM NAME LBRACE { enum_choice } RBRACE
    @_("ENUM NAME LBRACE { enum_choice } RBRACE")
    def enum_definition(self, p):
        return Enum(p.NAME, *p.enum_choice)

    # enum_choice : NAME SEMI
    #             | NAME LPAREN NAME RPAREN
    @_("NAME SEMI", "NAME LPAREN NAME RPAREN")
    def enum_choice(self, p):
        type = getattr(p, "NAME1", None)
        return Enum(p.NAME0, type)

    # if_statement : IF expression LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]
    @_("IF expression LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]")
    def if_statement(self, p):
        return If(p.expr, p.statements0, p.statements1)

    # if_let_statement : IF LET pattern ASSIGN expression LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]
    @_(
        "IF LET pattern ASSIGN expression LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]"
    )
    def if_let_statement(self, p):
        pass

    # while_statement : WHILE expr LBRACE statements RBRACE

    # while_let_statement : WHILE LET pattern ASSIGN expression LBRACE statements RBRACE

    # break_statement : BREAK SEMI

    # expression : orterm { LOR ortem }
    @_("orterm { LOR orterm }")
    def expression(self, p):
        if p.LOR:
            return BinOp("||", p.orterm0, p.orterm1)
        return p.orterm0

    # orterm : andterm { LAND andterm }
    @_("andterm { LAND andterm }")
    def orterm(self, p):
        if p.LAND:
            return BinOp("&&", p.andterm0, p.andterm1)
        return p.andterm0

    # andterm : sumterm { LT|LE|GT|GE|EQ|NE sumterm }
    @_(
        "sumterm { LT sumterm }",
        "sumterm { LE sumterm }",
        "sumterm { GT sumterm }",
        "sumterm { GE sumterm }",
        "sumterm { EQ sumterm }",
        "sumterm { NE sumterm }",
    )
    def andterm(self, p):
        if p[1]:
            return BinOp(p[1], p.sumterm0, p.sumterm1)
        return p.sumterm0

    # sumterm : multerm { PLUS|MINUS multerm }
    @_("multerm { PLUS  multerm }")
    def sumterm(self, p):
        if p.PLUS:
            return BinOp("+", p.multerm0, p.multerm1)
        return p.multerm0

    @_("multerm { MINUS multerm }")
    def sumterm(self, p):
        if p.MINUS:
            return BinOp("+", p.multerm0, p.multerm1)
        return p.multerm0

    # multerm : factor { TIMES|DIVIDE factor }
    @_("factor { DIVIDE factor }")
    def multerm(self, p):
        if p.DIVIDE:
            return BinOp("/", p.factor0, p.factor1)
        return p.factor0

    @_("factor { TIMES factor }")
    def multerm(self, p):
        if p.TIMES:
            return BinOp("*", p.factor0, p.factor1)
        return p.factor0

    # continue_statement : CONTINUE SEMI
    @_("CONTINUE SEMI")
    def continue_statement(self, p):
        return Continue()

    # return_statement : RETURN expression SEMI
    @_("RETURN expression SEMI")
    def return_statement(self, p):
        return Return(p.expression)

    # factor : literal
    #        | ....
    @_("location", "enum_value", "match", "literal")
    def factor(self, p):
        return p[0]

    @_("LPAREN expression RPAREN",)
    def factor(self, p):
        return Grouping(p.expression)

    @_(
        "PLUS expression", "MINUS expression", "LNOT expression",
    )
    def factor(self, p):
        return UnaryOp(p[1], p.expression)

    @_("NAME LPAREN exprlist RPAREN",)
    def factor(self, p):
        return FunctionCall(p.NAME, p.exprlist)

    @_("LBRACE statements RBRACE",)
    def factor(self, p):
        return p.statements

    # literal : INTEGER
    #         | FLOAT
    #         | CHAR
    #         | TRUE
    #         | FALSE
    #         | LPAREN RPAREN ? what to do here?

    @_("INTEGER")
    def literal(self, p):
        return Integer(int(p.INTEGER))

    @_("FLOAT")
    def literal(self, p):
        return Float(float(p.FLOAT))

    @_("CHAR")
    def literal(self, p):
        return Char(p.CHAR)

    @_("TRUE")
    def literal(self, p):
        return Truthy()

    @_("FALSE")
    def literal(self, p):
        return Falsey()

    # exprlist : expression { COMMA expression }
    #          | empty
    @_("expression { COMMA expression }")
    def exprlist(self, p):
        if p.expression1:
            return ExpressionList(*[p.expression0, p.expression1])
        return ExpressionList(p.expression0)

    @_("empty")
    def exprlist(self, p):
        return p.empty

    # location : NAME
    #          | expression DOT NAME
    @_("NAME")
    def location(self, p):
        return p.NAME

    @_("expression DOT NAME")
    def location(self, p):
        return DottedLocation(p.expression, p.NAME)

    # enum_value : NAME DCOLON NAME
    #            | NAME DCOLON NAME LPAREN expression RPAREN
    @_("NAME DCOLON NAME", "NAME DCOLON NAME LPAREN expression RPAREN")
    def enum_value(self, p):
        return EnumLocation(p.NAME0, p.NAME1, p.expression)

    # match : MATCH expression LBRACE { matchcase } RBRACE
    @_("MATCH expression LBRACE { matchcase } RBRACE")
    def match(self, p):
        return Match(p.expression, *p.matchcase)

    # matchcase : pattern ARROW expression SEMI
    @_("pattern ARROW expression SEMI")
    def matchcase(self, p):
        return MatchCondition(p.pattern, p.expression)

    # pattern   : NAME
    #           | NAME LPAREN NAME RPAREN
    @_("NAME LPAREN NAME RPAREN")
    def pattern(self, p):
        return Arguments(Argument(p.name0), Argument(p.name1))

    @_("NAME")
    def pattern(self, p):
        return p.NAME

    # type      : NAME
    @_("NAME")
    def type(self, p):
        return p.NAME

    # empty     :
    @_("")
    def empty(self, p):
        pass


# Top-level function that runs everything
def parse_source(text):
    tokens = tokenize(text)
    model = parse_tokens(tokens)  # You need to implement this part
    return model


# Example of a main program
def parse_file(filename):
    with open(filename) as file:
        text = file.read()
    return parse_source(text)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise SystemExit("Usage: wabbit.parse filename")
    model = parse(sys.argv[1])
    print(model)

