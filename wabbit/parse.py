# parse.py
#
# Wabbit parser.  The parser needs to construct the data model or an
# abstract syntax tree from text input.  The grammar shown here represents
# WabbitScript--a subset of the full Wabbit language.  It's written as
# a EBNF.  You will need to expand the grammar to include later features.
#
# Reference: https://github.com/dabeaz/compilers_2020_05/wiki/WabbitScript
#
# The following conventions are used:
# 
#	   ALLCAPS	   --> A token
#	   { symbols }   --> Zero or more repetitions of symbols
#	   [ symbols ]   --> Zero or one occurences of symbols (optional)
#	   s | t		 --> Either s or t (a choice)
#
#
# statements : { statement }
#
# statement : print_statement
#		   | assignment_statement
#		   | variable_definition
#		   | const_definition
#		   | if_statement
#		   | while_statement
#		   | break_statement
#		   | continue_statement
#		   | expr
#
# print_statement : PRINT expr SEMI
#
# assignment_statement : location ASSIGN expr SEMI
#
# variable_definition : VAR NAME [ type ] ASSIGN expr SEMI
#					 | VAR NAME type [ ASSIGN expr ] SEMI
#
# const_definition : CONST NAME [ type ] ASSIGN expr SEMI
#
# if_statement : IF expr LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]
#
# while_statement : WHILE expr LBRACE statements RBRACE
#
# break_statement : BREAK SEMI
#
# continue_statement : CONTINUE SEMI
#
# expr : expr PLUS expr		(+)
#	  | expr MINUS expr	   (-)
#	  | expr TIMES expr	   (*)
#	  | expr DIVIDE expr	  (/)
#	  | expr LT expr		  (<)
#	  | expr LE expr		  (<=)
#	  | expr GT expr		  (>)
#	  | expr GE expr		  (>=)
#	  | expr EQ expr		  (==)
#	  | expr NE expr		  (!=)
#	  | expr LAND expr		(&&)
#	  | expr LOR expr		 (||)
#	  | PLUS expr
#	  | MINUS expr
#	  | LNOT expr			  (!)
#	  | LPAREN expr RPAREN 
#	  | location
#	  | literal
#	  | LBRACE statements RBRACE 
#	   
# literal : INTEGER
#		 | FLOAT
#		 | CHAR
#		 | TRUE
#		 | FALSE
#		 | LPAREN RPAREN   
# 
# location : NAME
#
# type	  : NAME
#
# empty	 :
# ======================================================================

# How to proceed:  
#
# At first glance, writing a parser might look daunting. The key is to
# take it in tiny pieces.  Focus on one specific part of the language.
# For example, the print statement.  Start with something really basic
# like printing literals:
#
#	 print 1;
#	 print 2.5;
#
# From there, expand it to handle expressions:
#
#	 print 2 + 3 * -4;
#
# Then, expand it to include variable names
#
#	 var x = 3;
#	 print 2 + x;
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
#	- SLY (https://github.com/dabeaz/sly), 
#	- PLY (https://github.com/dabeaz/ply),
#	- ANTLR (https://www.antlr.org).

from .model import *
from .tokenize import tokenize, WabbitLexer
from sly import Parser


class WabbitParser(Parser):
	tokens = WabbitLexer.tokens			# token names from the lexer
	
	# program: statements
	@_('statements')
	def program(self, p):
		return p[0]

	# statements : { statement }
	#
	@_('{ statement }')
	def statements(self, p):
		# p.statement is a ist of "statement" objects
		return Statements(*p.statement)


	# statement : print_statement
	#		   | assignment_statement
	#		   | variable_definition
	#		   | const_definition
	#		   | if_statement
	#		   | while_statement
	#		   | break_statement
	#		   | continue_statement
	#		   | expr
	@_('print_statement',
		'assignment_statement',
#		'variable_definition', 
#		'const_definition',
#		'if_statement',
#		'while_statement',
#		'break_statement',
#		'continue_statement',
#		'expr'
	)
	def statement(tokens):
		return p[0]					# this is basically a pass through


	# print_statement : PRINT expr SEMI
	#
	@_('PRINT expr SEMI')
	def print_statement(self, p):		# p contains all the information from the parse
		# create node from the model
		return PrintStatement(p.expr)
		
	# assignment_statement : location ASSIGN expr SEMI
	#
	@_("location ASSIGN expr SEMI")
	def assignment_statement(tokens):
		return Assignment(p.location, p.expr)



	# variable_definition : VAR NAME [ type ] ASSIGN expr SEMI
	#					 | VAR NAME type [ ASSIGN expr ] SEMI
	@_("VAR NAME [ type ] ASSIGN expr SEMI")
	def variable_definition(self, p):
		return VarDef(p.NAME, p.type, p.expr)

	@_("VAR NAME type [ ASSIGN expr ] SEMI")
	def variable_definition(self, p):
		return VarDef(p.NAME, p.type, p.expr)

	#
	# const_definition : CONST NAME [ type ] ASSIGN expr SEMI
	#
	# if_statement : IF expr LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]
	#
	# while_statement : WHILE expr LBRACE statements RBRACE
	#
	# break_statement : BREAK SEMI
	#
	# continue_statement : CONTINUE SEMI
	#
	# expr : expr PLUS expr		(+)
	#	  | expr MINUS expr	   (-)
	#	  | expr TIMES expr	   (*)
	#	  | expr DIVIDE expr	  (/)
	#	  | expr LT expr		  (<)
	#	  | expr LE expr		  (<=)
	#	  | expr GT expr		  (>)
	#	  | expr GE expr		  (>=)
	#	  | expr EQ expr		  (==)
	#	  | expr NE expr		  (!=)
	#	  | expr LAND expr		(&&)
	#	  | expr LOR expr		 (||)
	#	  | PLUS expr
	#	  | MINUS expr
	#	  | LNOT expr			  (!)
	#	  | LPAREN expr RPAREN 
	#	  | location
	#	  | literal
	#	  | LBRACE statements RBRACE 
	
	@_("expr PLUS expr",
		"expr MINUS expr",
		"expr TIMES expr", 
		"expr DIVIDE expr")
	def expr(self, p):
		op = p[1]
		left = p.expression0
		right = p.expression1
		return BinOp(op, left, right)
		
	   
	# literal : INTEGER
	#		 | FLOAT
	#		 | CHAR
	#		 | TRUE
	#		 | FALSE
	#		 | LPAREN RPAREN   
	@_("INTEGER")
	def literal(self, p):
		return Integer(p.value)
		
	@_("FLOAT")
	def literal(self, p):
		return Float(p.value)

	@_("CHAR")
	def literal(self, p):
		return Char(p.value)
		
	@_("TRUE")
	def literal(self, p):
		return Bool(True)
		
	@_("FALSE")
	def literal(self, p):
		return Bool(False)
		
	@_("LPAREN RPAREN")
	def literal(self, p):
		return Unit()
	
	# location : NAME
	#
	@_("NAME")
	def location(tokens):
		return Var(tokens.NAME)


	# type	  : NAME
	#
	@_("NAME")
	def type(tokens):
		return tokens.NAME


	# empty	 :
	@_("")
	def empty(tokens):
		pass



# Top-level function that runs everything	
def parse_source(raw_tokens):
	parser = WabitParser()
	return parser.parse(raw_tokens)
	
	
# Example of a main program
def parse_file(filename):
	with open(filename) as file:
		text = file.read()
	return parse_source(text)

if __name__ == '__main__':
	import sys
	if len(sys.argv) != 2:
		raise SystemExit('Usage: wabbit.parse filename')
	model = parse(sys.argv[1])
	print(model)


