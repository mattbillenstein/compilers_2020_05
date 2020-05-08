class Environment				# class for handling scoping, variables, etc

	def __init__(self):
		self.variables = [{}]				# stack of variables scopes
		self.consts = [{}]					# stack of const(ants) scopes
		self.scopeLevel = 0					# current scope level
		
	def get(self, name):
		for i in range(self.scopeLevel, -1, -1):		# start at the top of the stack, work down
			if name in self.variables[i]:
				#print(f"get({name}) = {self.variables[i][name]} @ {i})")
				return self.variables[i][name]
			elif name in self.consts[i]:
				#print(f"getC({name}) = {self.consts[i][name]} @ {i})")
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
				#print(f"set({name}, {value}) @ {i})")
				return None
		
		# if we get here, we hit an error
		return f"unable to assign value to undeclared variable {name}"

		
	def addValue(self, name, value):
		#print (f"[{self.scopeLevel}] var {name} = {value}")
		# see if we have already defined a const with the same name in the current scope
		if name in self.consts[self.scopeLevel]:
			return f"{name} is a const at scope level {self.scopeLevel} and cannot be modified"
			
		if name in self.variables:
			return f"{name} is already defined in this scope"
		# add the new name/value to the current variables scope
		self.variables[self.scopeLevel][name] = value		
		return None
		
	def addConst(self, name, value):
		#print (f"[{self.scopeLevel}] const {name} = {value}")
		# see if we have already defined a const with the same name in the current scope
		if name in self.consts[self.scopeLevel]:
			return f"{name} is a const and cannot be modified"
			
			
		# add the new name/value to the current consts scope
		self.consts[self.scopeLevel][name] = value		
		return None
		
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
		