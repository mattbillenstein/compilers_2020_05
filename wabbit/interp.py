# interp.py
#
# In order to write a compiler for a programming language, it helps to
# have some kind of specification of how programs written in the
# programming language are actually supposed to work. A language is
# more than just "syntax" or a data model.  There has to be some kind
# of operational semantics that describe what happens when a program
# runs.
#
# One way to specify the operational semantics is to write a so-called
# "definitional interpreter" that directly executes the data
# model. This might seem like cheating--after all, our final goal is
# not to write an interpreter, but a compiler. However, if you can't
# write an interpreter, chances are you can't write a compiler either.
# So, the purpose of doing this is to pin down fine details as well as
# our overall understanding of what needs to happen when programs run.
#
# We'll write our interpreter in Python.  The idea is relatively 
# straightforward.  For each class in the model.py file, you're
# going to write a function similar to this:
#
#	def interpret_node_name(node, env):
#		# Execute "node" in the environment "env"
#		...
#		return result
#   
# The input to the function will be an object from model.py (node)
# along with an object respresenting the execution environment (env).
# The function will then execute the node in the environment and return
# a result.  It might also modify the environment (for example,
# when executing assignment statements, variable definitions, etc.). 
#
# For the purposes of this projrect, assume that all programs provided
# as input are "sound"--meaning that there are no programming errors
# in the input.  Our purpose is not to create a "production grade"
# interpreter.  We're just trying to understand how things actually
# work when a program runs. 
#
# For testing, try running your interpreter on the models you
# created in the example_models.py file.
#

from .model import *

"""
# Top level function that interprets an entire program. It creates the
# initial environment that's used for storing variables.

def interpret_program(model):
	# Make the initial environment (a dict)
	env = { }
	interpret(model, env)

# Internal function to interpret a node in the environment
def interpret(node, env):
	# Expand to check for different node types
	...
	raise RuntimeError(f"Can't interpret {node}")
"""	

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
		raise RuntimeException(f"{name} not defined before use")
		
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
				return
		
		# if we get here, we hit an error
		assert RuntimeError(f"unable to assign value to undeclared variable {name}")				

		
	def addValue(self, name, value):
		# see if we have already defined a const with the same name in the current scope
		if name in self.consts[self.scopeLevel]:
			raise RuntimeException(f"{name} is a const at scope level {self.scopeLevel} and cannot be modified")
			
		# add the new name/value to the current variables scope
		self.variables[self.scopeLevel][name] = value		
		
	def addConst(self, name, value):
		# see if we have already defined a const with the same name in the current scope
		if name in self.consts[self.scopeLevel]:
			raise RuntimeException(f"{name} is a const and cannot be modified")
			
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
		

		
class Interpreter:
	
	def __init__(self):
		self.env = Environment()		
		
	def interpret(self, node):
		methname = f'interpret_{node.__class__.__name__}'   
		fn = getattr(self, methname)

        # if we dont have a method... 
		if fn is None:
			raise RuntimeError(f"Can't interpret {node}") 
			
		# dispatch
		return fn(node)
		
	def interpret_(self, node):
		print("How the hell did you get here?!?!?!")
		pass	

	###
	### Literals
	###
			
	def interpret_Integer(self, node):
		return node.value
		
	def interpret_Float(self, node):
		return node.value
		
	def interpret_Char(self, node):
		return node.value
	
	def interpret_Bool(self, node):
		return node.value


	###
	### Expressions
	###
	
	def interpret_BinOp(self, node):
		leftval = self.interpret(node.left)
		rightval = self.interpret(node.right)
		
		# Do the operation
		if node.op == "+":
			return leftval + rightval
		elif node.op == "-":
			return leftval - rightval
		elif node.op == "*":
			return leftval * rightval
		elif node.op == "/":
			return leftval / rightval
		elif node.op == '<':
			return leftval < rightval
		elif node.op == '<=':
			return leftval <= rightval
		elif node.op == '>':
			return leftval > rightval
		elif node.op == '>=':
			return leftval >= rightval
		elif node.op == '==':
			return leftval == rightval
		elif node.op == '!=':
			return leftval != rightval			
			
		raise RuntimeError(f"Unknown op {node.op}")
		
	def interpret_UnaryOp(self, node):
		if node.op == "+":
			return self.interpret(node.right)
		elif node.op == "-":
			return -self.interpret(node.right)
		else:
			raise RuntimeError("Invalid UnaryOp: %s" % node.op)

	
	def interpret_LocationLookup(self, node):
		return self.env.get(node.var.name)
		
	
	def interpret_Grouping(self, node):
		return self.interpret(node.exprs)
		
		
	def interpret_Compound(self, node):
		retval = None
		self.env.increaseScope()
		retval = self.interpret(node.stmts)
		self.env.decreaseScope()
		return retval
					
	
	###
	### Locations
	###
	
	def interpret_Var(self, node):
		print(f"How did you get to a Var node? {node.name}")
	
	
	###
	### Statements
	###
	
	def interpret_ExpressionStatement(self, node):
		return self.interpret(node.expr)
		
		
	def interpret_Assignment(self, node):
		self.env.setValue(node.left.name, self.interpret(node.right))

		
	def interpret_PrintStatement(self, node):
		print(f"{self.interpret(node.literal)}")


	def interpret_Statements(self, node):
		result = None
		for stmt in node.stmts:
			result = self.interpret(stmt)
		return result
		
	def interpret_Block(self, node):
		result = None
		self.env.increaseScope()
		for stmt in node.stmts:
			result = self.interpret(stmt)
		self.env.decreaseScope()
		return result
	

	def interpret_ConstDef(self, node):
		self.env.addConst(node.name, self.interpret(node.value))
		
		
	def interpret_VarDef(self, node):
		value = 0
		if node.value is not None:
			value = self.interpret(node.value)
		self.env.addValue(node.name, value)
		

	def interpret_IfConditional(self, node):
		condition = self.interpret(node.condition)
		if condition:
			self.env.increaseScope()
			self.interpret(node.istrue)
			self.env.decreaseScope()

		else:
			if node.isfalse is not None:
				self.env.increaseScope()
				self.interpret(node.isfalse)
				self.env.decreaseScope()


	def interpret_While(self, node):
		condition = self.interpret(node.condition)
		while condition:
			self.env.increaseScope()
			self.interpret(node.todo)
			self.env.decreaseScope()
			condition = self.interpret(node.condition)
		
		
		
	###
	### The meta container ... Program
	###
	
	def interpret_Program(self, node):
		self.interpret_Statements(node.stmts)