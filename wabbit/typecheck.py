# typecheck.py
#
# Type Checking
# =============
# This file implements type checking. Wabbit uses what's known as
# "nomimal typing."  That means that types are given unique
# names such as "int", "float", "bool", etc. Two types are the same
# if they have exactly the same name.  That's it.
#
# In implementing the type checker, the best strategy might be to
# not overthink the problem at hand. Basically, you have type names.
# You can represent these names using Python strings and compare them
# using string comparison. This gives you most of what you need.
#
# In some cases, you might need to check combinations of types against a
# large number of cases (such as when implementing the math operators).
# For that, it helps to make lookup tables.  For example, you can use
# Python dictionaries to build lookup tables that encode valid
# combinations of binary operators.  For example:
#
# _binops = {
#	 # ('lefttype', 'op', 'righttype') : 'resulttype'
#	 ('int', '+', 'int') : 'int',
#	 ('int', '-', 'int') : 'int',
#	 ...
# }
#
# The directory tests/Errors has Wabbit programs with various errors.

from .model import *



class Environment:
	def __init__(self):
		self.variables = [{}]				# stack of variables scopes
		self.consts = [{}]					# stack of const(ants) scopes
		self.scopeLevel = 0					# current scope level
		
	def get(self, name):
		for i in range(self.scopeLevel, -1, -1):		# start at the top of the stack, work down
			if name in self.variables[i]:
				return self.variables[i][name]
			elif name in self.consts[i]:
				return self.consts[i][name]
		
		# if you get down here, you didnt find the variable
		print(f"{name} is not defined within scope")
		return None

		
	def setValue(self, name, value):
		constLevel = -1		# if this stays at -1, then we dont have a const defined with the name
		
		# check to see if the variable name is used as a constant at some higher level
		for i in range(self.scopeLevel, -1, -1):		# start at the top of the stack, work down
			if name in self.consts[i]:
				constLevel = i
				break
				
		# see if the variable exists in the various levels of variables (but not so far down that it hits the const def, if any)
		for i in range(self.scopeLevel, constLevel, -1):
			if name in self.variables[i]:				
				self.variables[i][name] = value
				return None
		
		# if we get here, we hit an error
		return f"unable to assign value to undeclared variable {name}"

		
	def addValue(self, name, value):
		# see if we have already defined a const with the same name in the current scope
		if name in self.consts[self.scopeLevel]:
			return f"{name} is a const at scope level {self.scopeLevel} and cannot be modified"
			
		if name in self.variables:
			return f"{name} is already defined in this scope"
		# add the new name/value to the current variables scope
		self.variables[self.scopeLevel][name] = value		
		return None
		
	def addConst(self, name, value):
		# see if we have already defined a const with the same name in the current scope
		if name in self.consts[self.scopeLevel]:
			print(f"{name} is a const and cannot be modified")
			
		# add the new name/value to the current consts scope
		self.consts[self.scopeLevel][name] = value		
		
	def increaseScope(self):
		# increase the scope level
		self.scopeLevel += 1
		
		# add a new scope to the stack
		self.variables.append({})
		self.consts.append({})
		
	def decreaseScope(self):
		# clear out the current scope's entries
		del(self.variables[self.scopeLevel])
		del(self.consts[self.scopeLevel])
		
		# decrease the scope level
		self.scopeLevel -= 1
		
		# sanity check
		if self.scopeLevel < 0:
			raise RuntimeError(f"Invalid scope! scopeLevel = {self.scopeLevel}")
		

		
class WabbitChecker:
	
	_bin_ops = {
				('+', 'int', 'int') : 'int',
				('-', 'int', 'int') : 'int',
				('+', 'float', 'float') : 'float',
				('-', 'float', 'float') : 'float',
				('<', 'int', 'int') : 'bool',
				('<=', 'int', 'int') : 'bool',
				('>', 'int', 'int') : 'bool',
				('>=', 'int', 'int') : 'bool',
				('==', 'int', 'int') : 'bool',
				('!=', 'int', 'int') : 'bool',
				('<', 'float', 'float') : 'bool',
				('<=', 'float', 'float') : 'bool',
				('>', 'float', 'float') : 'bool',
				('>=', 'float', 'float') : 'bool',
				('==', 'float', 'float') : 'bool',
				('!=', 'float', 'float') : 'bool',
				("&&", "bool", "bool") : 'bool',
				("!", "bool", "bool") : 'bool',
				("||", "bool", "bool") : "bool"
	}
	correct = True			# set to false on any error
	inWhile = False			# indicator if the interpreter is currently inside a while loop


	def __init__(self):
		self.env = Environment()		
		
	def check(self, node):
		methname = f'check_{node.__class__.__name__}'   
		fn = getattr(self, methname)

		# if we dont have a method... 
		if fn is None:
			raise RuntimeError(f"Can't check {node}") 
			
		# dispatch
		return fn(node)
		
	def check_(self, node):
		print("How the hell did you get here?!?!?!")
		pass	

	###
	### Literals
	###
			
	def check_Integer(self, node):
		node.valtype = "int"
		return "int"
		
	def check_Float(self, node):
		node.valtype = "int"
		return "float"
		
	def check_Char(self, node):
		node.valtype = "int"
		return "char"
	
	def check_Bool(self, node):
		node.valtype = "int"
		return "bool"

	def check_Unit(self, node):
		node.valtype = "unit"
		return "unit"


	###
	### Expressions
	###
	
	def check_BinOp(self, node):
		lefttype = self.check(node.left)
		righttype = self.check(node.right)
		
		valtype = self._bin_ops.get((node.op, lefttype, righttype))
		if valtype is None:
			self.correct = False
			print(f"type error: {lefttype} {node.op} {righttype} is illegal")

		# set the type for the node
		node.valtype = valtype

		return valtype

		
	def check_UnaryOp(self, node):
		valtype = self.check(node.right)
		if node.op in {"+", "-"} and valtype in {"int", "float"}:
			node.valtype = valtype
			return valtype
			
		elif node.op == "!" and valtype == "bool":
			node.valtype = valtype
			return valtype
		else:
			self.correct = False
			node.valtype = None
			print(f"type error: {valtype} not compatiable with {node.op} operation")

	
	def check_LocationLookup(self, node):
		valtype = self.env.get(node.var.name)
		if valtype == None:
			self.correct = False
			print(f"Syntax Error. {node.var.name} does not exist within scope")

		node.valtype = valtype
		return valtype
		
	
	def check_Grouping(self, node):
		valtype = self.check(node.expr)
		node.valtype = valtype
		return valtype

		
		
	def check_Compound(self, node):
		valtype = None
		self.env.increaseScope()
		valtype = self.check(node.stmts)
		self.env.decreaseScope()
		node.valtype = valtype
		return retval
					
	
	###
	### Locations
	###
	
	def check_Var(self, node):
		print(f"How did you get to a Var node? {node.name}")
	
	
	###
	### Statements
	###
	
	def check_ExpressionStatement(self, node):
		return self.check(node.expr)
		
		
	def check_Assignment(self, node):
		rightval = self.check(node.right)
		leftval = self.check(node.left)
		if rightval is None:
			print(f"Error in expression: {node.right.to_source}")
			
		self.env.setValue(node.left.name, node.right)

		
	def check_PrintStatement(self, node):
		self.check(node.expr)
		return Unit()


	def check_Statements(self, node):
		result = None
		for stmt in node.stmts:
			result = self.check(stmt)
		return result
		
	def check_Block(self, node):
		result = None
		self.env.increaseScope()
		for stmt in node.stmts:
			result = self.check(stmt)
		self.env.decreaseScope()
		return result
	

	def check_ConstDef(self, node):
		vartype = "unit"
		valtype = "unit"

		if node.value is not None:
			valtype = self.check(node.value)

		if node.vartype is not None:
			vartype = node.vartype
		
		if valtype != node.vartype:
			self.correct = False
			print(f"Type Error: Unable to assign {valtype} type object to {vartype} object")
		
		err = self.env.addConst(node.name, vartype)
		if err is not None:
			self.correct = False
			print (f"Syntax Error: {err}")		
		
	def check_VarDef(self, node):

		vartype = "unit"
		valtype = "unit"

		if node.value is not None:
			valtype = self.check(node.value)

		if node.vartype is not None:
			vartype = node.vartype
		
		print(node, vartype, valtype)
		if node.value is not None and valtype != node.vartype:
			self.correct = False
			print(f"Type Error: Unable to assign {valtype} type object to {vartype} object")
		
		err = self.env.addValue(node.name, vartype)
		if err is not None:
			self.correct = False
			print (f"Syntax Error: {err}")
		

	def check_IfConditional(self, node):
		condition = self.check(node.condition)
		if condition != "bool":
			self.correct = False
			print(f"Invalid Syntax: {node.condition.to_source()} is not a bool")
		
		self.env.increaseScope()
		self.check(node.istrue)
		self.env.decreaseScope()		
		
		if node.isfalse is not None:
			self.env.increaseScope()
			self.check(node.isfalse)
			self.env.decreaseScope()


	def check_While(self, node):
		condition = self.check(node.condition)
		if condition != "bool":
			self.correct = False
			print(f"Invalid Syntax: {node.condition.to_source()} is not a bool")

		self.env.increaseScope()
		self.inWhile = True
		self.check(node.todo)
		self.inWhile = False
		self.env.decreaseScope()
		
	def check_BreakStatement(self, node):
		if self.inWhile == False:
			self.correct == False
			print("Invalid Syntax: break statement outside of a while loop")

	def check_ContinueStatement(self, node):
		if self.inWhile == False:
			self.correct == False
			print("Invalid Syntax: continue statement outside of a while loop")

			
	###
	### The meta container ... Program
	###
	
	def check_Program(self, node):
		self.check_Statements(node.stmts)


# Top-level function used to check programs
def check_program(model):
	checker = WabbitChecker()
	checker.check(model)
	return checker.correct

# Sample main program
def main(filename):
	from .parse import parse_file
	model = parse_file(filename)
	print(check_program(model))

if __name__ == '__main__':
	import sys
	main(sys.argv[1])



		


		
