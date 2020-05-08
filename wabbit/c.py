# c.py
#
# In this file, we're going to transform Wabbit code to C, using it as
# a kind of low-level machine language. At first glance, this might
# sound somewhat crazy, but it actually makes sense for a number of
# reasons.  First, C compilers are standardized and ubiquitous--being
# available everywhere. Second, C is so minimal in features that you
# can use it at a low-level without having to worry about hidden
# side-effects (i.e., garbage collection, etc.).  You can also abuse
# it all sorts of horrible ways to do unnatural acts of programming
# (useful if making a new language).  Finally, in getting
# your compiler to actually "work", there may be certain runtime
# elements that are quite hard to implement or debug directly with machine
# instructions. Therefore, it might be easier to implement things in C 
# as a first step.
#
# As a preliminary step, please read the short C tutorial at
#
#  https://github.com/dabeaz/compilers_2020_05/wiki/C-Programming-Tutorial
#
# Come back here when you've looked it over.  Our goal is to produce
# low-level C code where you are ONLY allowed to use the 
# the following C features:
#
# 1. You can only declare uninitialized variables.  For example:
# 
#		 int x;
#		 float y;
#		 int z = 2 + 3;	 // NO!!!!!!!!
#
#	All variables must be declared before use, at the top of the
#	file or function. Reminder: they are uninitialized.
#
# 2. You can only perform ONE operation at a time. Operations can
#	only involve constants and variabless.  The result of an
#	operation must always be immediately stored in a variable.  For
#	example, to compute 2 + 3 * 4, you might do this:
#
#		 int _i1;	  /* Temporary variables */
#		 int _i2;
#
#		 _i1 = 3 * 4;
#		 _i2 = 2 + i1;
#
# 3. The only allowed control flow constucts are the following two 
#	statements:
#
#		goto Label;
#		if (_variable) goto Label;
#
#		Label:
#		   ... code ...
#
#	No, you don't get "else". And you also don't get code blocks 
#	enclosed in braces { }. 
#
# 4. You may print things with printf().
#
# That's it, those are the only C features you may use.  To help you
# out, Here's a small fragment of Wabbit code that executes a loop:
#
#	/* Sample Wabbit Code */
#	/* Print the first 10 factorials */
#
#	var result = 1;
#	var n = 1;
#
#	while n <= 10 {
#		result = result * n;
#		print result;
#		n = n + 1;
#	}
#
# Here's what the corresponding C code might look like (it can vary
# as long as you object the general rules above):
#
#	#include <stdio.h>
#
#	int result;	   
#	int n;
#
#	int main() {
#		int _i1;
#		int _i2;
#		int _i3;
#
#		result = 1;
#		n = 1;
#	L1:
#		_i1 = (n <= 10);
#		if (_i1) goto L2;
#		goto L3;
#	L2:
#		_i2 = result * n;
#		result = _i2;
#		printf("%i\n", result);
#		_i3 = n + 1;
#		n = _i3;
#		goto L1;
#	L3:
#		return 0;
#	}
#		 
# One thing to keep in mind... the goal is NOT to produce code for
# humans to read.  Instead, it's to produce code that is minimal and
# which can be reasoned about. There is very little actually happening
# in the above code.  It has calculations and gotos. That is basically
# it.  There is no unseen high-level magic going on. What you see
# it what it is.

# Hints:
# ------
# In the compileer, you wrote code that just "did the operation"
# right there.  You used Python as the runtime environment.  In the
# type-checker, you wrote code that merely "checked the operation" to
# see if there were any errors.  In this project, you have to do a bit
# of both.  For each object in your model, you're going to write a
# function that *creates* the code for carrying out the operation.
# This will be very similar to the compileer.  However, in order to
# create this code, you've got to know a few things about types. So,
# that information has to be tracked as well.  In addition, there's
# going to be a bit of extra bookkeeping related to the environment.
# For instance, in the above example, extra "C variables" such as
# "_i1", "_i2" and "_i3" are created to hold temporary values.  You'll
# need to have some way to keep track of that.
#
# Also, one other thing... everything that happens here takes place
# *after* type-checking.  Therefore, you don't need to focus on
# problem related to incorrect programs. Assume that all programs
# are fully correct with respect to their usage of types and names.

from .model import *
from collections import ChainMap



class CFunction:
	
	def __init__(self, name, parent = None):
		self.name = name
		self.parent = parent		# the parent environment
		self.locals = ""			# local variables
		self.statements = ""		# statements 
		self.stack = [ ]			# stack for variables/values from expressions ... an "expression stack"
		self.labelNum = 0			# index for labels
		self.varNum = 0				# index for var identifiers
		self.env = ChainMap()		# for tracking variables

		
	def push(self, value):
		self.stack.append(value)
		
	def pop(self):
		return self.stack.pop()
		
	def convertType(self, t):
		if t in ("float", "char"):
			return t
		return "int"
		
	def getVarName(self, node):
		return f"_t{node.nodename}"
		
	def getNewLabel(self):
		self.labelNum += 1
		return f"L{self.labelNum}"
		
	def __str__(self):
		return (f"int {self.name}()" + "{\n" + self.locals + "\n" + self.statements + "}\n")
		
	
	
class WabbitToC:

	def __init__(self):
		self.c = CFunction("main")
		
	def compile(self, node):
		methname = f'compile_{node.__class__.__name__}'   
		fn = getattr(self, methname)

		# if we dont have a method... 
		if fn is None:
			raise RuntimeError(f"Can't compile {node}") 
			
		# dispatch
		return fn(node)
		
	def compile_(self, node):
		print("How the hell did you get here?!?!?!")
		pass	

	###
	### Literals
	###
			
	def compile_Integer(self, node):
		self.c.push(node.value)
		
	def compile_Float(self, node):
		self.c.push(node.value)
		
	def compile_Char(self, node):
		node.valtype = "int"
		self.c.push(ord(node.value))
	
	def compile_Bool(self, node):
		node.valtype = "int"
		self.c.push(int(node.value))
		


	###
	### Expressions
	###
	
	def compile_BinOp(self, node):
		self.compile(node.left)			# pushes result to stack
		self.compile(node.right)		# pushes result to stack
		rightval = self.c.pop()			# get the right side from the stack
		leftval = self.c.pop()			# get the left side from the stack
		lvar = self.c.getVarName(node)
		self.c.locals += f"{self.c.convertType(node.valtype)} {lvar};\n"
		self.c.statements += f"{lvar} = {leftval} {node.op} {rightval};  // {node}\n"
		self.c.push(lvar);

		
	def compile_UnaryOp(self, node):
		self.compile(node.right)		# pushes result to stack
		rightval = self.c.pop()			# get the right side from the stack
		lvar = self.c.getVarName(node)
		self.c.locals += f"{self.c.convertType(node.valtype)} {lvar};\n"
		self.c.statements += f"{lvar} = {node.op}{rightval};  // {node}\n"
		self.c.push(lvar);


	def compile_LocationLookup(self, node):
		self.c.push(f"_t{node.var.nodename}")
		
		
	def compile_Grouping(self, node):
		self.compile(node.expr)
		
		
	def compile_Compound(self, node):
		self.c.statements += "{\n"
		# increase scope
		self.compile(node.stmts);
		# decrease scope
		self.c.statements += "}\n"

	
	###
	### Locations
	###
	
	def compile_Var(self, node):
		print(f"How did you get to a Var node? {node.name}")
	
	
	###
	### Statements
	###
	
	def compile_ExpressionStatement(self, node):
		self.compile(node.expr)
		
		
	def compile_Assignment(self, node):
		self.compile(node.right)
		self.c.statements += f"{self.c.getVarName(node.left)} = {self.c.pop()};  // {node}\n"

		
	def compile_PrintStatement(self, node):
		self.compile(node.expr)
		exprval = self.c.pop()
		if node.expr.valtype == "int":
			self.c.statements += f"printf(\"%d\", {exprval});  // {node}\n"
		elif node.expr.valtype == "float":
			self.c.statements += f"printf(\"%f\", {exprval});  // {node}\n"
		elif node.expr.valtype == "char":
			self.c.statements += f"printf(\"%c\", {exprval});  // {node}\n"
		elif node.expr.valtype == "bool":
			self.c.statements += f"printf(\"%i\", {exprval});  // {node}\n"


	def compile_Statements(self, node):
		result = None
		for stmt in node.stmts:
			self.compile(stmt)
			if isinstance(stmt, ExpressionStatement):
				result = self.c.pop()
			else:
				result = None
		if result:
			self.c.push(result)
			

	def compile_Block(self, node):
		self.compile(stmt)
		"""
		result = None
		self.env.increaseScope()
		for stmt in node.stmts:
			result = self.compile(stmt)
		self.env.decreaseScope()
		return result
		"""

	def compile_ConstDef(self, node):
		self.c.env[node.nodename] = node
		self.c.locals += f"const {self.c.convertType(node.valtype)} {self.c.getVarName(node)};  // {node}\n"
		if node.value is not None:
			self.compile(node.value)
			val = self.c.pop()
			self.c.statements += f"{self.c.getVarName(node)} = {val};\n"
		#self.env.addConst(node.name, self.compile(node.value))
		
		
	def compile_VarDef(self, node):
		self.c.env[node.nodename] = node
		self.c.locals += f"{self.c.convertType(node.valtype)} {self.c.getVarName(node)};  // {node}\n"
		if node.value is not None:
			self.compile(node.value)
			val = self.c.pop()
			self.c.statements += f"{self.c.getVarName(node)} = {val};\n"
		#self.env.addValue(node.name, value)
		

	def compile_IfConditional(self, node):
		self.compile(node.condition)				# conditional statement is now on the stack
		istrueLabel = f"L{self.c.getNewLabel()}"
		isfalseLabel = f"L{self.c.getNewLabel()}"
		completionLabel = f"L{self.c.getNewLabel()}"
			
		self.c.statements += f"if ({self.c.pop()}) goto {istrueLabel}; // {node}\n"
		self.c.statements += f"goto {isfalseLabel};\n"
		
		self.c.statements += f"{istrueLabel}: //{node.istrue}\n"
		self.c.statements += "{\n"
		self.compile(node.istrue)
		self.c.statements += "}\n"
		self.c.statements += f"goto {completionLabel}\n"
		self.c.statements += f"{isfalseLabel}: //{node.isfalse}\n"
		if node.isfalse is not None:
			self.c.statements += "{\n"			
			self.compile(node.isfalse)
			self.c.statements += "}\n"
			
		self.c.statements +=f"{completionLabel}:\n"
			

	def compile_While(self, node):
		self.compile(node.condition)				# conditional statement is now on the stack
		condLabel = f"L{self.c.getNewLabel()}"
		bodyLabel = f"L{self.c.getNewLabel()}"
		exitLabel = f"L{self.c.getNewLabel()}"
			
		self.c.statements += f"{condLabel}:  // {node}\n"
		self.compile(node.condition)				# push condition expression to stack
		
		self.c.statements += f"if ({self.c.getVarName(node.condition)}) goto {bodyLabel};\ngoto {exitLabel};\n"
		self.c.statements += f"{bodyLabel}: //{node.todo}\n"
		self.c.statements += "{\n"
		# increase scope
		self.c.env['break'] = exitLabel
		self.c.env['continue'] = condLabel
		self.compile(node.todo)
		self.c.statements += "}"
		self.c.statements += f"goto {condLabel};\n" 
		
		self.c.statements += f"{exitLabel}:\n"
		
		
	def compile_BreakStatement(self, node):
		self.c.statements += f"goto {self.c.env['break']};  // {node}\n"
		
	def compile_ContinueStatement(self, node):
		self.c.statements += f"goto {self.c.env['continue']};  // {node}\n"
		
	###
	### The meta container ... Program
	###
	
	def compile_Program(self, node):
		self.compile_Statements(node.stmts)	
		
# Top-level function to handle an entire program.
def compile_program(model):
	compiler = WabbitToC()
	compiler.compile(model)
	return str(compiler.c)
	

def main(filename):
	from .parse import parse_file
	from .typecheck import check_program

	model = parse_file(filename)
	check_program(model)
	code = compile_program(model)
	with open('out.c', 'w') as file:
		file.write("#include <stdio.h>\n")
		file.write(code)
	print('Wrote: out.c')

if __name__ == '__main__':
	import sys
	main(sys.argv[1])

