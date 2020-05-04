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


class Integer:
	'''
	Example: 42
	'''
	def __init__(self, value):
		self.value = value

	def __repr__(self):
		return f'Integer({self.value})'

	def to_source(self):
		return repr(self.value)
		
	
class Float:
	'''
	Example: 42
	'''
	def __init__(self, value):
		self.value = value

	def __repr__(self):
		return f'Float({self.value})'

	def to_source(self):
		return repr(self.value)
		
		
class BinOp:
	'''
	Example: left + right
	'''
	def __init__(self, op, left, right):
		self.op = op
		self.left = left
		self.right = right

	def __repr__(self):
		return f'BinOp({self.op}, {self.left}, {self.right})'
		
	def to_source(self):
		return f'{self.left.to_source()} {self.op} {self.right.to_source()}'

class UnaryOp:
	'''
	Example: left + right
	'''
	def __init__(self, op, right):
		self.op = op
		self.right = right

	def __repr__(self):
		return f'UnaryOp({self.op}, {self.right})'
		
	def to_source(self):
		return f'{self.op}{self.right.to_source()}'


class Assignment:
	'''
	Example: a = 1 + 2
	'''
	
	def __init__(self, left, right):
		self.left = left
		self.right = right
		
	def __repr__(self):
		return f'Assign({self.left}, {self.right})'
		
	def to_source(self):
		return f'{self.left.to_source()} = {self.right.to_source()}'
		
		
class PrintStatement:
	def __init__(self, literal):
		self.literal = literal
		
	def __repr__(self):
		return f'PrintStatement({self.literal})'
		
	def to_source(self):
		return f"print {self.literal.to_source()}"

class Program:
	'''
	Container for a program
	'''
	
	def __init__(self, stmts):
		self.stmts = stmts
		
	def __repr__(self):
		return "Program(" + ",".join([repr(x) for x in self.stmts]) + ")"
		
	def to_source(self):
		return "\n".join([x.to_source() for x in self.stmts])
	
class Block:	
	'''
	block of code
	'''
	
	def __init__(self, stmts):
		self.stmts = stmts
		
	def __repr__(self):
		return "Block(" + ",".join([repr(x) for x in self.stmts]) + ")"
		
	def to_source(self):
		return "{\n" + "\n".join([x.to_source() for x in self.stmts]) + "}\n"

class Statement:
	'''
	adsfsadf;
	'''
	def __init__(self, expr):
		self.expr = expr
		
	def __repr__(self):
		return f"Expr({self.expr}"
		
	def to_source(self):
		return f'{self.expr.to_source()};'
	
class ConstDef:
	'''
	const a
	'''
	
	def __init__(self, name):
		self.name = name
		
	def __repr__(self):
		return f"ConstDef({repr(self.name)})"
		
	def to_source(self):
		return f"const {self.name.to_source()}"
	

class VarDef:
	def __init__(self, name, vartype = ""):
		self.name = name
		self.vartype = vartype
		
	def __repr__(self):
		return f"VarDef({self.name}, {self.vartype})"
		
	def to_source(self):
		return f"var {self.name} {self.vartype} "
	

class Var:
	def __init__(self, name):
		self.name = name
		
	def __repr__(self):
		return f"Var({self.name})"
		
	def to_source(self):
		return f"{self.name}"


class IfConditional:
	def __init__(self, condition, istrue, isfalse = None):
		self.condition = condition
		self.istrue = istrue
		self.isfalse = isfalse

	def __repr__(self):
		if self.isfalse is None:
			return f"IfConditional({self.condition}, {self.istrue})"
		return f"IfConditional({self.condition}, {self.istrue}, {self.isfalse})"
		
	def to_source(self):
		output = f"if {self.condition.to_source()}\n{self.istrue.to_source()}"
		if self.isfalse is not None:
			output += f"{self.isfalse.to_source()}"
		return output
		

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



	
