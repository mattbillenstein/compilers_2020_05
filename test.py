class Node:
	def __init__(self, lineno = -1, nodename = None, valtype = None):
		self.lineno = lineno				# point in the source code where the node originated
		self.nodename  = nodename			# used for identifying specific nodes by "name"
		self.valtype = valtype 				# used for tracking the type associated with a node in the model
		print(lineno)

class Integer(Node):
	def __init__(self, value, **options):
		assert isinstance(value, int)
		self.vartype = "int"
		self.value = value
		print(options['lineno'])
		options['lineno'] = 744
		super().__init__(**options)
		
		
		
Integer(1, lineno=123)