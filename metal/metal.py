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
            op, *args = self.instructions[self.registers['PC']]
            # Uncomment to debug what's happening
            # print(self.registers['PC'], op, args)
            # print(self.registers)
            # print()
            if self.registers['PC'] == 23:
                print('multiply', self.memory[self.registers['R5']:self.registers['R5'] + 10])
                # throw('fran')
            if self.registers['PC'] == 49:
                # print('factorial', self.registers)
                print('factorial', self.memory[self.registers['R5']:self.registers['R5'] + 10])
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
        print('STORE', rs, rd, offset, addr, self.registers[rs])
        self.memory[self.registers[rd]+offset] = self.registers[rs]
        if addr == IO_OUT:
            print(self.registers[rs])

    def JMP(self, rd, offset):
        print('JMP', rd, offset, self.registers[rd] + offset)
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
    # machine.run(prog1)
    print(":::PROGRAM 1 DONE")

    # ----------------------------------------------------------------------
    # Problem 2: Computation
    #
    # Write a Metal program that computes 3 * 7.
    #
    # Note: The machine doesn't implement multiplication. So, you need
    # to figure out how to do it.  Hint:  You can use one of the values
    # as a counter.
    # so we're gonna dec oneside, add the other side, jump back
    # and with some sort of mask we're gonna jump to store and halt when oneside hits 0
    # oh no that's what bz does, ok

    prog2 = [ # Instructions here
              ('CONST', 3, 'R1'),             #1
              ('CONST', 7, 'R2'),             #2
              ('CONST', 0, 'R3'),             #3 the value
              ('CONST', 4, 'R4'),             #4 where to jump to (ie after this line)
              ('ADD', 'R2', 'R3', 'R3'),      #5
              ('DEC', 'R1'),                  #6
              ('BZ', 'R1', 1),                #7 if R1 hits 0, skip the next line
              ('JMP', 'R4', 0),               #8 jump back
              ('STORE', 'R3', 'R0', IO_OUT),
              ('HALT',),
            ]

    print("PROGRAM 2::: Expected Output: 21")
    # machine.run(prog2)
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
        ('CONST', 5, 'R1'),
        ('CONST', 1, 'R2'),
        ('STORE', 'R1', 'R0', 101),     # set x arg for mul
        ('STORE', 'R2', 'R0', 102),     # set y arg for mul
        ('CONST', 6, 'R3'),             # significant line number (where to come back to)
        ('JMP', 'R0', 12),              # significant line number (start of mul)
        ('LOAD', 'R0', 'R2', 104),      # read result
        ('DEC', 'R1'),
        ('BZ', 'R1', 1),
        ('JMP', 'PC', -8),
        ('STORE', 'R2', 'R0', IO_OUT),
        ('HALT',),

        ('STORE', 'R1', 'R0', 200),     # multiply function
        ('STORE', 'R2', 'R0', 201),
        ('STORE', 'R3', 'R0', 202),
        ('STORE', 'R4', 'R0', 203),
        ('STORE', 'R5', 'R0', 204),
        ('STORE', 'R6', 'R0', 205),

        ('LOAD', 'R0', 'R1', 101),
        ('LOAD', 'R0', 'R2', 102),
        ('CONST', 0, 'R3'),
        ('ADD', 'R2', 'R3', 'R3'),
        ('DEC', 'R1'),
        ('BZ', 'R1', 1),
        ('JMP', 'PC', -4),
        ('STORE', 'R3', 'R0', 104),     # set return value

        ('LOAD', 'R0', 'R1', 200),
        ('LOAD', 'R0', 'R2', 201),
        ('LOAD', 'R0', 'R3', 202),
        ('LOAD', 'R0', 'R4', 203),
        ('LOAD', 'R0', 'R5', 204),
        ('LOAD', 'R0', 'R6', 205),
        ('JMP', 'R3', 0),               # return to caller
    ]

    print("PROGRAM 3::: Expected Output: 120")
    # machine.run(prog3)
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

    # ok so for a recursive call we're gonna have to store the arguments at
    # different memory locations (but not the return val?)
    # which means we have to keep a depth count, and then also have a way of turning
    # that count into a location, AND the location has to be different from the other
    # function, same for the register state, so we get a register value and add 100 to it

    # every time I call a function I need to know
    #  1) what line number to jump to
    #  2) where to put the arguments (including which line number to jump back to)
    #  3) where to read the return value from
    #  4) I can trust a function to put the registers back exactly as they were

    # [return val, line to return to, args...] gets written to memory[0 + offset tot + 1 incr of offset]

    # when I am a function I need to know
    #  1) where to read the arguments (including which line number to jump back to)
    #  2) where to write the return value
    # [return val, line to return to, args...] read from [ 0 + offset tot]

    # so let's say that each function gets 50 consecutive addresses of memory
    # how do we give the function call its unique offset?

    # each function has a call counter, how many times is it currently being called
    # at a hardcoded memory location
    # each function calls unique memory offset is at (50 * number of functions * current call count)

    # but of course there's no multiply so
    # each function stores its current offset, and incrs it by 50 * num functions when it's called
    #   and decrs it by same when it's all done
    # when you call a function and get its return val you have to look at addresses 1 greater 50 * num functions

    # so mul's val goes at -1
    # fact's goes at -2
    # the step size is 50 * 2 = 100
    prog4 = [
        # initialize where to find unique memory addresses for each function call
        ('CONST', 0, 'R1'),
        ('STORE', 'R1', 'R7', -1), # mul's call offset
        ('CONST', 50, 'R1'),
        ('STORE', 'R1', 'R7', -2), # factorial's call offset
        ('CONST', 100, 'R6'), # Don't touch R6 it always has the offset step size
                              # also reserve R5 as the current offset
        # start processing main
        # we're gonna call fact, find the memory address offset for this call
        ('LOAD', 'R7', 'R4', -2),
        # set args for fact function call
        ('CONST', 11, 'R1'),          # line num to return to    LINE NO
        ('STORE', 'R1', 'R4', 101),  # memory addresses are offset step size bigger for calling
        ('CONST', 5, 'R1'),          # n = 5
        ('STORE', 'R1', 'R4', 102),
        ('JMP', 'R0', 41),              # 10 # call fact             LINE NO
        ('LOAD', 'R4', 'R1', 100),      # read result
        ('STORE', 'R1', 'R0', IO_OUT),
        ('HALT',),

        # multiply function
        # incr memory offset for this call
        ('LOAD', 'R7', 'R5', -1), # current offset val
        ('ADD', 'R6', 'R5', 'R5'),# add step size
        ('STORE', 'R5', 'R7', -1), #store it
        # R5 is our unique memory address now

        # put the registers in memory
        ('STORE', 'R1', 'R5', 40),
        ('STORE', 'R2', 'R5', 41),
        ('STORE', 'R3', 'R5', 42),
        ('STORE', 'R4', 'R5', 43), #20

        ('LOAD', 'R5', 'R1', 2), # read x
        ('LOAD', 'R5', 'R2', 3),  # read y
        ('CONST', 0, 'R3'), # initialize result
        ('BZ', 'R1', 8),
        ('DEC', 'R1'),
        ('CONST', 31, 'R4'),            #                              LINE NO
        ('STORE', 'R4', 'R5', 101),     # set line to return to
        ('STORE', 'R1', 'R5', 102),     # set x arg for mul
        ('STORE', 'R2', 'R5', 103),     # set y arg for mul
        ('JMP', 'R0', 14),           #30   # call mul                     LINE NO
        ('LOAD', 'R5', 'R3', 100),      # read result
        ('ADD', 'R2', 'R3', 'R3'),
        ('STORE', 'R3', 'R5', 0),      # set return value

        # put the registers back as they were
        ('LOAD', 'R5', 'R1', 40),
        ('LOAD', 'R5', 'R2', 41),
        ('LOAD', 'R5', 'R3', 42),
        ('LOAD', 'R5', 'R4', 43),
        ('LOAD', 'R5', 'R4', 1),      # load line number to return to
        ('SUB', 'R5', 'R6', 'R5'),
        ('JMP', 'R4', 0),           #40    # return to caller

        # factorial function
        # incr memory offset for this call
        ('LOAD', 'R7', 'R5', -2), # current offset val
        ('ADD', 'R6', 'R5', 'R5'),# add step size
        ('STORE', 'R5', 'R7', -2), #store it
        # R5 is our unique memory address now

        # put the registers in memory
        ('STORE', 'R1', 'R5', 40),
        ('STORE', 'R2', 'R5', 41),
        ('STORE', 'R3', 'R5', 42),
        ('STORE', 'R4', 'R5', 43),

        ('LOAD', 'R5', 'R1', 2), # read n
        ('CONST', 0, 'R3'),      # initialize return
        ('BZ', 'R1', 22),        # 50 # if R1 is 0 return 1
        # when I wanna call mul, what's its address?
        ('LOAD', 'R7', 'R4', -1),
        ('STORE', 'R1', 'R4', 102),     # set x arg for mul

        ('DEC', 'R1'),
        # now I wanna call fact
        ('CONST', 58, 'R2'),           # LINE NO
        ('STORE', 'R2', 'R5', 101),     # set line to return to
        ('STORE', 'R1', 'R5', 102),     # set n arg for factorial
        ('JMP', 'R0', 41),              # call fact LINE NO
        ('LOAD', 'R5', 'R3', 100),      # read result

        # back to calling mul R4 is mul's address
        # R4 gets messed up because we use it to return to line number, so reload it
        ('LOAD', 'R7', 'R4', -1),
        ('STORE', 'R3', 'R4', 103),     # set y arg for mul
        ('CONST', 64, 'R2'),        # 60    #           LINE NO
        ('STORE', 'R2', 'R4', 101),     # set line to return to
        ('JMP', 'R0', 14),              # call mul LINE NO
        ('LOAD', 'R4', 'R3', 100),      # read result
        ('STORE', 'R3', 'R5', 0),      # set return value

        # put the registers back as they were
        ('LOAD', 'R5', 'R1', 40),
        ('LOAD', 'R5', 'R2', 41),
        ('LOAD', 'R5', 'R3', 42),
        ('LOAD', 'R5', 'R4', 43),
        # decr unique call offset by step size
        ('LOAD', 'R5', 'R4', 1),      # 70 # load line number to return to
        ('SUB', 'R5', 'R6', 'R5'),
        ('JMP', 'R4', 0),               # return to caller

        # else return 1
        ('INC', 'R1'),
        ('STORE', 'R1', 'R5', 0),

        # put the registers back as they were
        ('LOAD', 'R5', 'R1', 40),
        ('LOAD', 'R5', 'R2', 41),
        ('LOAD', 'R5', 'R3', 42),
        ('LOAD', 'R5', 'R4', 43),
        ('LOAD', 'R5', 'R4', 1),      # load line number to return to
        ('SUB', 'R5', 'R6', 'R5'),
        ('JMP', 'R4', 0),             #80  # return to caller
        ]

    # we can no longer have 1 hardcoded memory address for the function, instead
    # we have hardcoded offsets to set the args in and keep a depth offset and depth count
    # in two registers
    mul_recursive = [
        ('CONST', 5, 'R1'),
        ('CONST', 7, 'R2'),
        ('CONST', 0, 'R6'),
        ('CONST', 100, 'R5'),
        ('STORE', 'R1', 'R6', 111),     # set x arg for mul
        ('STORE', 'R2', 'R6', 112),     # set y arg for mul
        ('CONST', 8, 'R4'),             # significant line number (where to come back to)
        ('JMP', 'R0', 11),              # significant line number (start of mul)
        ('LOAD', 'R6', 'R1', 114),      # read result
        ('STORE', 'R1', 'R0', IO_OUT),
        ('HALT',),

        ('ADD', 'R6', 'R5', 'R6'),      # multiply function
        ('STORE', 'R1', 'R6', 0),
        ('STORE', 'R2', 'R6', 1),
        ('STORE', 'R3', 'R6', 2),
        ('STORE', 'R4', 'R6', 3),

        ('LOAD', 'R6', 'R1', 11),
        ('LOAD', 'R6', 'R2', 12),
        ('CONST', 0, 'R3'),
        ('BZ', 'R1', 7),
        ('DEC', 'R1'),
        ('STORE', 'R1', 'R6', 111),     # set x arg for mul
        ('STORE', 'R2', 'R6', 112),     # set y arg for mul
        ('CONST', 25, 'R4'),            # significant line number (where to come back to)
        ('JMP', 'R0', 11),              # significant line number (start of mul)
        ('LOAD', 'R6', 'R3', 114),      # read result
        ('ADD', 'R2', 'R3', 'R3'),
        ('STORE', 'R3', 'R6', 14),      # set return value

        ('LOAD', 'R6', 'R1', 0),
        ('LOAD', 'R6', 'R2', 1),
        ('LOAD', 'R6', 'R3', 2),
        ('LOAD', 'R6', 'R4', 3),
        ('SUB', 'R6', 'R5', 'R6'),
        ('JMP', 'R4', 0),               # return to caller

        ]

    print("PROGRAM 4::: Expected Output: 120")
    machine.run(prog4)
    print(":::PROGRAM 4 DONE")
