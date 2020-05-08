# model.py
#
# This file defines the data model for Wabbit programs.  The data
# model is a data structure that represents the contents of a program
# as objects, not text.  Sometimes this structure is known as an
# "abstract syntax tree" or AST.  However, the model is not
# necessarily directly tied to the actual syntax of the language.  So,
# we'll prefer to think of it as a more generic data model instead.
#
# To do this, you need to identify the different "elements" that make
# up a program and encode them into classes.  To do this, it may be
# useful to slightly "underthink" the problem. To illustrate, suppose
# you wanted to encode the idea of "assigning a value."  Assignment
# involves a location (the left hand side) and a value like this:
#
#		 location = expression;
#
# To represent this idea, make a class with just those parts:
#
#	 class Assignment:
#		 def __init__(self, location, expression):
#			 self.location = location
#			 self.expression = expression
#
# What are "location" and "expression"?  Does it matter? Maybe
# not. All you know is that an assignment operator definitely requires
# both of those parts.  DON'T OVERTHINK IT.  Further details will be
# filled in as the project evolves.
# 
# Work on this file in conjunction with the top-level
# "script_models.py" file.  Go look at that file and see what program
# samples are provided.  Then, figure out what those programs look like 
# in terms of data structures.
#
# There is no "right" solution to this part of the project other than
# the fact that a program has to be represented as some kind of data
# structure that's not "text."   You could use classes. You could use 
# tuples. You could make a bunch of nested dictionaries like JSON. 
# The key point: it must be a data structure.
#
# Starting out, I'd advise against making this file too fancy. Just
# use basic data structures. You can add usability enhancements later.
# -----------------------------------------------------------------------------

# The following classes are used for the expression example in script_models.py.
# Feel free to modify as appropriate.  You don't even have to use classes
# if you want to go in a different direction with it.


# Base types

class Node:
	def __init__(self, *, lineno = -1, nodename = None, valtype = None):
		self.lineno = lineno				# point in the source code where the node originated
		self.nodename  = nodename			# used for identifying specific nodes by "name"
		self.valtype = valtype 				# used for tracking the type associated with a node in the model
	
class Statement(Node):
	'''
	statement object
	'''
	
class Expression(Node):
	'''
	somethig that produces a value
	'''
	
class Literal(Expression):
	'''
	container for literals such as integers, floats, etc.
	'''
class Definition(Statement):
	'''
	used for defining things like names
	'''
	
class Location(Node):
	'''
	a place to store/load values
	'''

###
### Highest level container
###

class Program(Node):
	def __init__(self, stmts):
		assert isinstance(stmts, Statements)
		self.stmts = stmts
		
	def __repr__(self):
		return f"Program({self.stmts})"
		
	def to_source(self):
		return self.stmts.to_source();

###
### LITERAL-typed nodes
###
	
class Integer(Literal):
	'''
	Example: 42
	'''
	def __init__(self, value, **kwargs):
		assert isinstance(value, int)
		self.value = value
		kwargs['valtype'] = "int"
		super().__init__(**kwargs)

	def __repr__(self):
		return f'Integer({self.value})'

	def to_source(self):
		return repr(self.value)
		
	
class Float(Literal):
	'''
	Example: 42.0
	'''
	def __init__(self, value, **kwargs):
		assert isinstance(value, float)
		kwargs['valtype'] = "float"
		self.value = value
		super().__init__(**kwargs)
		
	def __repr__(self):
		return f'Float({self.value})'

	def to_source(self):
		return repr(self.value)
		
		
class Char(Literal):
	'''
	Example: 'a'
	'''
	def __init__(self, value, **kwargs):
		assert isinstance(value, str)
		kwargs['valtype'] = "char"
		self.value = value
		super().__init__(**kwargs)
				
	def __repr__(self):
		return f'Char({self.value})'

	def to_source(self):
		return self.value
		
class Bool(Literal):
	'''
	Example: true
	'''
	def __init__(self, value, **kwargs):
		assert isinstance(value, bool)
		kwargs['valtype'] = "bool"
		self.value = value
		super().__init__(**kwargs)

	def __repr__(self):
		return f'Bool({self.value})'

	def to_source(self):
		return str(self.value)
		
		
class Unit(Literal):
	'''
	Example: ()
	'''
	
	def __init__(self, **kwargs):
		kwargs['valtype'] = "unit"
		self.value = None
		super().__init__(**kwargs)
		
	def __repr__(self):
		return f'Unit()'
		
	def to_source(self):
		return '()'
	
	
###
### Expressions
###

class BinOp(Expression):
	'''
	Example: left + right
	'''
	def __init__(self, op, left, right, **kwargs):
		super().__init__(**kwargs)
		assert isinstance(left, Expression)
		assert isinstance(right, Expression)
		self.op = op
		self.left = left
		self.right = right

	def __repr__(self):
		return f'BinOp({self.op}, {self.left}, {self.right})'
		
	def to_source(self):
		return f'{self.left.to_source()} {self.op} {self.right.to_source()}'

class UnaryOp(Expression):
	'''
	Example: left + right
	'''
	def __init__(self, op, right, **kwargs):
		super().__init__(**kwargs)
		self.op = op
		self.right = right

	def __repr__(self):
		return f'UnaryOp({self.op}, {self.right})'
		
	def to_source(self):
		return f'{self.op}{self.right.to_source()}'

class LocationLookup(Expression):
	'''
	converts a location (expression) to a statement
	'''
	
	def __init__(self, var, **kwargs):
		super().__init__(**kwargs)
		assert isinstance(var, Location)
		self.var = var
		
	def __repr__(self):
		return f"LocationLookup({self.var})"
		
	def to_source(self):
		return self.var.to_source()

class Compound(Expression):
	'''
	A series of statements serving as a single expression.
	'''
	def __init__(self, stmts, **kwargs):
		super().__init__(**kwargs)
		assert isinstance(stmts, Statements)
		self.stmts = stmts

	def __repr__(self):
		return f'Compound({self.stmts})'	
		
	def to_source(self):
		return '{\n' + self.stmts.to_source() + '\n}'
		
class Grouping(Expression):
	'''
	( expression )      # Expression surrounded by parenthesis
	'''
	def __init__(self, expr, **kwargs):
		super().__init__(**kwargs)
		assert isinstance(expr, Expression)
		self.expr = expr

	def __repr__(self):
		return f'Grouping({self.expr})'
		
	def to_source(self):
		return f"({self.expr})"
		

###
### Locations
###


class Var(Location):
	def __init__(self, name, **kwargs):
		super().__init__(**kwargs)
		assert isinstance(name, str)
		self.name = name
		
	def __repr__(self):
		return f"Var({self.name})"
		
	def to_source(self):
		return f"{self.name}"
			

###
### Statements
###
		
class Statements(Statement):
	'''
	Container for statements
	'''
	
	def __init__(self, *args, **kwargs):
		super().__init__(**kwargs)
		stmts = [x for x in args]
		assert all(isinstance(x, Statement) for x in stmts)
		self.stmts = stmts
		
	def __repr__(self):
		return f"Statements([id={self.nodename}]" + ",".join([repr(x) for x in self.stmts]) + ")"
		
	def to_source(self):
		return "\n".join([x.to_source() for x in self.stmts])


class Assignment(Statement):
	'''
	Example: a = 1 + 2
	'''
	
	def __init__(self, left, right, **kwargs):
		super().__init__(**kwargs)
		assert isinstance(left, Location)
		assert isinstance(right, Expression)
		self.left = left
		self.right = right
		
	def __repr__(self):
		return f'Assign({self.left}, {self.right})'
		
	def to_source(self):
		return f'{self.left.to_source()} = {self.right.to_source()};'
		
		
class PrintStatement(Statement):
	def __init__(self, expr, **kwargs):
		super().__init__(**kwargs)
		self.expr = expr
		
	def __repr__(self):
		return f'PrintStatement({self.expr})'
		
	def to_source(self):
		return f"print {self.expr.to_source()};"


class Block(Statement):	
	'''
	block of code
	'''
	
	def __init__(self, *args, **kwargs):
		super().__init__(**kwargs)
		stmts = [x for x in args]
		assert all(isinstance(x, Statement) for x in stmts)
		self.stmts = stmts
		
	def __repr__(self):
		return "Block(" + ",".join([repr(x) for x in self.stmts]) + ")"
		
	def to_source(self):
		return "{\n" + "\n".join([x.to_source() for x in self.stmts]) + "\n}\n"

	
class ConstDef(Statement):
	'''
	const a
	'''
	
	def __init__(self, name, valtype, value, **kwargs):
		super().__init__(**kwargs)
		assert isinstance(name, str)
		assert valtype is None or isinstance(valtype, str)
		assert isinstance(value, Expression)
		self.name = name
		self.valtype = valtype
		self.value = value		

	def __repr__(self):
		return f"ConstDef({self.name}, {self.valtype}, {self.value})"
		
	def to_source(self):
		if self.valtype is None:
			return f"const {self.name} = {self.value.to_source()};"
		return f"const {self.name} {self.valtype} = {self.value.to_source()};"


class VarDef(Statement):
	def __init__(self, name, valtype, value = None, **kwargs):
		super().__init__(**kwargs)
		assert isinstance(name, str)
		assert valtype is None or isinstance(valtype, str)
		assert value is None or isinstance(value, Expression)
		assert not (valtype is None and value is None)
		self.name = name				# name of the variable
		self.valtype = valtype			# the type of variable (int, float, etc...)
		self.value = value				# if the value had an assignment, this is the expr assigned to .name variable
		
	def __repr__(self):
		return f"VarDef({self.name}, {self.valtype}, {self.value})"
		
	def to_source(self):
		src = f"var {self.name}"
		if self.valtype is not None:
			src += f" {self.valtype}"
		if self.value is not None:
			src += f" = {self.value.to_source()}"
		src += ";"
		return src


class IfConditional(Statement):
	def __init__(self, condition, istrue, isfalse = None, **kwargs):
		super().__init__(**kwargs)
		assert isinstance(condition, Expression)
		assert isinstance(istrue, Statement)
		assert isfalse is None or isinstance(isfalse, Statement)
		self.condition = condition
		self.istrue = istrue
		self.isfalse = isfalse

	def __repr__(self):
		if self.isfalse is None:
			return f"IfConditional({self.condition}, {self.istrue})"
		return f"IfConditional({self.condition}, {self.istrue}, {self.isfalse})"
		
	def to_source(self):
		output = f"if {self.condition.to_source()} {self.istrue.to_source()}"
		if self.isfalse is not None:
			output += f"else {self.isfalse.to_source()}"
		return output
		

class While(Statement):
	def __init__(self, condition, todo, **kwargs):
		super().__init__(**kwargs)
		assert isinstance(condition, Expression)
		assert isinstance(todo, Statement)
		self.condition = condition
		self.todo = todo

	def __repr__(self):
		return f"While({self.condition}, {self.todo})"
		
	def to_source(self):
		return f"while {self.condition.to_source()} {self.todo.to_source()}"
		
		
class BreakStatement(Statement):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		
	def __repr__(self):
		return f"Break()"
		
	def to_source(self):
		return f"break;"
		
class ContinueStatement(Statement):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		
	def __repr__(self):
		return f"ContinueStatement()"
		
	def to_source(self):
		return f"continue;"
		
		
class ExpressionStatement(Statement):
	def __init__(self, expr, **kwargs):
		super().__init__(**kwargs)
		#print(expr)
		assert isinstance(expr, Expression)
		self.expr = expr
	
	def __repr__(self):
		return f"ExpressionStatement({self.expr})"
		
	def to_source(self):
		return f"{self.expr.to_source()};"

# ------ Debugging function to convert a model into source code (for easier viewing)

def to_source(node):
	return node.to_source()
	print(node.to_source())

	if isinstance(node, Integer):
		return node.to_source()
	elif isinstance(node, BinOp):
		return node.to_source()
	else:
		raise RuntimeError(f"Can't convert {node} to source")



	
