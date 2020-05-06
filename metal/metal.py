# metal.py
# 
# One of the main roles of a compiler is taking high-level programs
# such as what you might write in C or Python and reducing them to
# instructions that can execute on actual hardware.
#
# This file implements a very tiny CPU in the form of a Python
# program.  Although simulated, this CPU mimics the behavior of a real
# CPU.  There are registers for performing simple mathematical
# calculations, memory operations for loading/storing values, control
# flow instructions for branching and gotos, and an I/O port for
# performing output.
#
# See the end of this file for some exercises.
#
# The CPU has 8 registers (R0, R1, ..., R7) that hold 32-bit unsigned
# integer values.  Register R0 is hardwired to always contains the
# value 0. Register R7 is initialized to the highest valid memory
# address. A special register PC holds the index of the next
# instruction that will execute.
#
# The memory of the machine consists of 65536 memory slots,
# each of which can hold an integer value.  Special LOAD/STORE
# instructions access the memory.  Instructions are stored 
# separately.  All memory addresses from 0-65535 may be used.
#
# The machine has a single I/O port which is mapped to the memory
# address 65535 (0xFFFF).  The symbolic constant IO_OUT contains the
# value 65535 and can be used when writing code.  Writing an integer
# to this address causes the integer value to be printed to terminal.
# This can be useful for debugging.
#
# The machine understands the following instructions--which
# are encoded as tuples:
#
#   ('ADD', 'Ra', 'Rb', 'Rd')       ; Rd = Ra + Rb
#   ('SUB', 'Ra', 'Rb', 'Rd')       ; Rd = Ra - Rb
#   ('INC', 'Ra')                   ; Ra = Ra + 1
#   ('DEC', 'Ra')                   ; Ra = Ra - 1
#   ('AND', 'Ra', 'Rb', 'Rd')       ; Rd = Ra & Rb (bitwise-and)
#   ('OR', 'Ra', 'Rb', 'Rd')        ; Rd = Ra | Rb (bitwise-or)
#   ('XOR', 'Ra', 'Rb', 'Rd')       ; Rd = Ra ^ Rb (bitwise-xor)
#   ('SHL', 'Ra', 'Rb', 'Rd')       ; Rd = Ra << Rb (left bit-shift)
#   ('SHR', 'Ra', 'Rb', 'Rd')       ; Rd = Ra >> Rb (right bit-shift)
#   ('CMP', 'Ra', 'Rb', 'Rd')       ; Rd = (Ra == Rb) (compare)
#   ('CONST', value, 'Rd')          ; Rd = value
#   ('LOAD', 'Rs', 'Rd', offset)    ; Rd = MEMORY[Rs + offset]
#   ('STORE', 'Rs', 'Rd', offset)   ; MEMORY[Rd + offset] = Rs
#   ('JMP', 'Rd', offset)           ; PC = Rd + offset
#   ('BZ', 'Rt', offset)            ; if Rt == 0: PC = PC + offset
#   ('HALT,)                        ; Halts machine
#
# In the the above instructions 'Rx' means some register number such
# as 'R0', 'R1', etc.  The 'PC' register may also be used as a register.
# All memory instructions take their address from register plus an offset 
# that's encoded as part of the instruction.

IO_OUT = 65535
MASK = 0xffffffff

class Metal:
    def run(self, instructions):
        '''
        Run a program. memory is a Python list containing the program
        instructions and other data.  Upon startup, all registers
        are initialized to 0.  R7 is initialized with the highest valid
        memory index (len(memory) - 1).
        '''
        self.registers = { f'R{d}':0 for d in range(8) }
        self.registers['PC'] = 0
        self.instructions = instructions
        self.memory = [0] * 65536
        self.registers['R7'] = len(self.memory) - 2
        self.running = True
        while self.running:
            if self.registers['PC'] == 5: print("mul(%d, %d):" % (self.registers['R1'], self.registers['R2']))
            if self.registers['PC'] == 22: print("fact(%d):" % self.registers['R1'])
        		
            op, *args = self.instructions[self.registers['PC']]
            # Uncomment to debug what's happening
            print("%02d: %05s %20s ; %s %s" % (self.registers['PC'], op, args, " ".join(["'%s': %02d," % (x, self.registers[x]) for x in self.registers.keys()]), self.memory[self.registers['R7']:]))
            self.registers['PC'] += 1
            getattr(self, op)(*args)
            self.registers['R0'] = 0    # R0 is always 0 (even if you change it)
        return

    def ADD(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] + self.registers[rb]) & MASK

    def SUB(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] - self.registers[rb]) & MASK

    def INC(self, ra):
        self.registers[ra] = (self.registers[ra] + 1) & MASK

    def DEC(self, ra):
        self.registers[ra] = (self.registers[ra] - 1) & MASK

    def AND(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] & self.registers[rb]) & MASK

    def OR(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] | self.registers[rb]) & MASK

    def XOR(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] ^ self.registers[rb]) & MASK

    def SHL(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] << self.registers[rb]) & MASK

    def SHR(self, ra, rb, rd):
        self.registers[rd] = (self.registers[ra] >> self.registers[rb]) & MASK

    def CMP(self, ra, rb, rd):
        self.registers[rd] = int(self.registers[ra] == self.registers[rb])

    def CONST(self, value, rd):
        self.registers[rd] = value & MASK

    def LOAD(self, rs, rd, offset):
        self.registers[rd] = (self.memory[self.registers[rs]+offset]) & MASK

    def STORE(self, rs, rd, offset):
        addr = self.registers[rd]+offset
        self.memory[self.registers[rd]+offset] = self.registers[rs]
        if addr == IO_OUT:
            print(self.registers[rs])

    def JMP(self, rd, offset):
        self.registers['PC'] = self.registers[rd] + offset

    def BZ(self, rt, offset):
        if not self.registers[rt]:
            self.registers['PC'] += offset

    def HALT(self):
        self.running = False

# =============================================================================

if __name__ == '__main__':        
    machine = Metal()

    # ----------------------------------------------------------------------
    # Program 1:  Computers
    #
    # The CPU of a computer executes low-level instructions.  Using the
    # Metal instruction set above, show how you would compute 3 + 4 - 5
    # and print out the result.
    # 

    prog1 = [ # Instructions here
              ('CONST', 3, 'R1'),
              ('CONST', 4, 'R2'),
              ('ADD', 'R1', 'R2', 'R1'),
              ('CONST', 5, 'R2'),
              ('SUB', 'R1', 'R2', 'R1'),
              # Print the result.  Change R1 to location of result.
              ('STORE', 'R1', 'R0', IO_OUT),    
              ('HALT',),
              ]

    print("PROGRAM 1::: Expected Output: 2")
    machine.run(prog1)
    print(":::PROGRAM 1 DONE")

    # ----------------------------------------------------------------------
    # Problem 2: Computation
    #
    # Write a Metal program that computes 3 * 7.
    #
    # Note: The machine doesn't implement multiplication. So, you need
    # to figure out how to do it.  Hint:  You can use one of the values
    # as a counter. 

    prog2 = [ # Instructions here
              ('CONST', 3, 'R1'),
              ('CONST', 7, 'R2'),
              ('ADD', 'R2', 'R3', 'R3'),		# R3 is initialized to 0 at startup, acting as our accumulator now
              ('DEC', 'R1'),
              ('BZ', 'R1', 1),
              ('JMP', 'PC', -4),					# R4 is initialized to 0 at startup
              # Print result. Change R1 to location of result
              ('STORE', 'R3', 'R0', IO_OUT),
              ('HALT',),
            ]

    print("PROGRAM 2::: Expected Output: 21")
    machine.run(prog2)
    print(':::PROGRAM 2 DONE')

    # ----------------------------------------------------------------------
    # Problem 3: Abstraction and functions
    #
    # A major part of programming concerns abstraction. One of the most
    # common tools of abstraction is the concept of a function/procedure.
    # For example, consider this high-level Python code:
    #
    #    def mul(x, y):
    #        result = 0
    #        while x > 0:
    #            result += y
    #            x -= 1
    #        return result
    #
    #    n = 5
    #    result = 1
    #    while n > 0:
    #        result = mul(result, n)
    #        n -= 1
    #
    # How would you encode something like this into machine code?
    # Specifically.  How would you define the function mul(). How
    # would it receive inputs?  How would it return a value?  How
    # would the branching/jump statements work?  

    prog3 = [
        # result = 1
        # while n > 0:
        #     result = mul(result,  n)
        #     n -= 1

        ('CONST', 5, 'R1'),			# n = 5
        ('CONST', 1, 'R2'),			# result
        
        ('BZ', 'R1',  6),		# while n > 0
        ('STORE', 'PC', 'R7', 0),	# set up CALL by saving current PC to stack
        ('JMP', 'R0', 11),			# make the CALL
        
        ('STORE', 'R6', 'R7', 0),	# save return val to stack
        ('LOAD', 'R7', 'R2', 0),	# put the return in the result register
        
        ('DEC', 'R1'),				# n--
        ('JMP', 'R0', 2),			# loop

        # print(result)
        ('STORE', 'R2', 'R0', IO_OUT),   # R2 Holds the Result
        ('HALT',),

        # ----------------------------------
        # ; mul(x, y) -> x * y
        # 
        #    def mul(x, y):
        #        result = 0
        #        while x > 0:
        #            result += y
        #            x -= 1
        #        return result
        #
        # ... instructions here
        # inputs are R1: x, R2: y
        # output in R6
        
        # Addr = 12
        
        ('DEC', 'R7'),						# start the PUSH
        ('STORE', 'R1', 'R7', 0),			# PUSH R1 to the stack since we modify it 
        
        ('CONST', 0, 'R6'),					# initialize accum
        ('ADD', 'R2', 'R6', 'R6'),
        ('DEC', 'R1'),
        ('BZ', 'R1', 1),
        ('JMP', 'PC', -4),					# R4 is initialized to 0 at startup

		('LOAD', 'R7', 'R1', 0),			# POP the R1 value off the stack
		('INC', 'R7'),						# finish the POP

		('LOAD', 'R7', 'R5', 0),			# pop return address from the stack
        
        ('JMP', 'R5', 1)					# RET
        
    ]

    print("PROGRAM 3::: Expected Output: 120")
    machine.run(prog3)
    print(":::PROGRAM 3 DONE")
    
    # ----------------------------------------------------------------------
    # Problem 4: Ultimate Challenge
    #
    # How would you modify Problem 3 to make a recursive function work?
    #
    #    def mul(x, y):
    #        if x > 0:
    #            return y + mul(x-1, y)
    #        else:
    #            return 0
    #
    #    def fact(n):
    #        if n == 0:
    #            return 1
    #        else:
    #            return mul(n, fact(n-1))
    #    
    #    print(fact(5))

    prog4 = [
        ('CONST', 5, 'R1'),    	
        ('STORE', 'PC', 'R7', 0),	# set up CALL by saving current PC to stack
        ('JMP', 'R0', 22),			# make the CALL to fact()
        # Print result (assumed to be in R1)
        ('STORE', 'R6', 'R0', IO_OUT),
        ('HALT',),

		#    def mul(x, y):
		#        if x > 0:
		#            return y + mul(x-1, y)
		#        else:
		#            return 0

		# addr = 5	mul function
		('CONST', 0, 'R5'),			# prologue
		('SUB', 'R7', 'R5', 'R7'),
		('STORE', 'R1', 'R7', 1),	# x
		('STORE', 'R2', 'R7', 2),	# y
		
		('BZ', 'R1', 5),			# if !(x > 0) ... 

		('DEC', 'R1'),				# x--
		('STORE', 'PC', 'R7', 0),	#	save retaddr
		('JMP', 'R0', 5),			# 	CALL mul
		('ADD', 'R6', 'R2', 'R6'),	# y + mul(x-1, y)
		('JMP', 'PC', 1),
		
		('CONST', 0, 'R6'),			# x == 0: return 0
		
		('LOAD', 'R7', 'R1', 1), 	# restore x
		('LOAD', 'R7', 'R2', 2),	# restore y
		
		('CONST', 3, 'R5'),
		('ADD', 'R7', 'R5', 'R7'),	# epilogue
		
		('LOAD', 'R7', 'R5', 0),		# RET
		('JMP', 'R5', 1),
		


		# addr = 22
        #    def fact(n):
        #        if n == 0:
        #            return 1
        #        else:
        #            return mul(n, fact(n-1))
    	('CONST', 3, 'R5'),			# prologue
		('SUB', 'R7', 'R5', 'R7'),
		('STORE', 'R1', 'R7', 1),	# n
		('STORE', 'R2', 'R7', 2),	# tmp = n
		
		('BZ', 'R1', 9),
		('DEC', 'R1'),
		('LOAD', 'R7', 'R2', 1),		# y = n
		
		('STORE', 'PC', 'R7', 0),	#	save retaddr
		('JMP', 'PC', -9),			# 	CALL fact
		
		('STORE', 'R6', 'R7', 0),	
		('LOAD', 'R7', 'R1', 0),	# MOV R1, R6
		
		('STORE', 'PC', 'R7', 0),	#	save retaddr
		('JMP', 'R0', 5),			# 	CALL mul
		('JMP', 'PC', 1),
		
		('CONST', 1, 'R6'),			# return 1
		
		('LOAD', 'R7', 'R1', 1), 	# restore n
		('LOAD', 'R7', 'R2', 2),	# restore tmp
		
		('CONST', 3, 'R5'),
		('ADD', 'R7', 'R5', 'R7'),	# epilogue
		
		('LOAD', 'R7', 'R5', 0),	# RET
		('JMP', 'R5', 1)
        ]

    print("PROGRAM 4::: Expected Output: 120")
    machine.run(prog4)
    print(":::PROGRAM 4 DONE")
