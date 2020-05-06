# tokenizer.py
#
# The role of a tokenizer is to turn raw text into recognized symbols 
# known as tokens. 
#
# The following set of tokens are defined for "WabbitScript".  Later
# parts of the project require you to add more tokens.  The suggested
# name of the token is on the left. The matching text is on the right.
#
# Reserved Keywords:
#	 CONST   : 'const'
#	 VAR	 : 'var'  
#	 PRINT   : 'print'
#	 BREAK   : 'break'
#	 CONTINUE: 'continue'
#	 IF	  : 'if'
#	 ELSE	: 'else'
#	 WHILE   : 'while'
#	 TRUE	: 'true'
#	 FALSE   : 'false'
#
# Identifiers/Names
#	 NAME	: Text starting with a letter or '_', followed by any number
#			   number of letters, digits, or underscores.
#			   Examples:  'abc' 'ABC' 'abc123' '_abc' 'a_b_c'
#
# Literals:
#	 INTEGER :  123   (decimal)
#
#	 FLOAT   : 1.234
#			   .1234
#			   1234.
#
#	 CHAR	: 'a'	 (a single character - byte)
#			   '\xhh'  (byte value)
#			   '\n'	(newline)
#			   '\''	(literal single quote)
#
# Operators:
#	 PLUS	 : '+'
#	 MINUS	: '-'
#	 TIMES	: '*'
#	 DIVIDE   : '/'
#	 LT	   : '<'
#	 LE	   : '<='
#	 GT	   : '>'
#	 GE	   : '>='
#	 EQ	   : '=='
#	 NE	   : '!='
#	 LAND	 : '&&'
#	 LOR	  : '||'
#	 LNOT	 : '!'
#	
# Miscellaneous Symbols
#	 ASSIGN   : '='
#	 SEMI	 : ';'
#	 LPAREN   : '('
#	 RPAREN   : ')'
#	 LBRACE   : '{'
#	 RBRACE   : '}'
#
# Comments:  To be ignored
#	  //			 Skips the rest of the line
#	  /* ... */	  Skips a block (no nesting allowed)
#
# Errors: Your lexer may optionally recognize and report the following
# error messages:
#
#	  lineno: Illegal char 'c'		 
#	  lineno: Unterminated character constant	
#	  lineno: Unterminated comment
#
# ----------------------------------------------------------------------


from sly import Lexer	  # Disclaimer: I created SLY

class WabbitLexer(Lexer):
	# Valid token names
	tokens = { 
	
		# keywords
		CONST, VAR, PRINT, BREAK, CONTINUE, IF, ELSE, WHILE, TRUE, FALSE,
		
		# identifiers
		NAME, 
		
		# literals
		INTEGER, FLOAT, CHAR, 
		
		# operators
		PLUS, MINUS, TIMES, DIVIDE, LT, LE, GT, GE, EQ, NE, LAND, LOR, LNOT,
		
		# misc. 
		ASSIGN, SEMI, LPAREN, RPAREN, LBRACE, RBRACE, DOT,
		
		}
	ignore = ' \t'	   # Ignore these (between tokens)
	ignore_line_comment = r'//.*'

	# Line number tracking
	@_(r'\n+')
	def ignore_newline(self, t):
		self.lineno += t.value.count('\n')

	@_(r'/\*(.|\n)*?\*/')
	def ignore_block_comment(self, t):
		self.lineno += t.value.count('\n')
		

	# Specify tokens as regex rules
	NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
	PLUS = r'\+'
	MINUS = r'-'
	TIMES = r'\*'
	DIVIDE = r'/'
	INTEGER = r'\d+'

	@_(r'\d+')
	def INTEGER(self, t):
		t.value = int(t.value)   # Convert to a numeric value
		return t

	@_(r'(\d+\.\d*)|(\d*\.\d+)')
	def FLOAT(self, t):
		t.value = float(t.value)
		return t


	# Put longer patterns first
	LAND = r'&&'
	LOR = r'\|\|'
	EQ = r'=='
	NE = r'!='
	LE = r'<='
	GE = r'>='
	LT = r'<'			   # Order matters a lot. Definition order is the order matches are tried.
	GT = r'>'
	LNOT = r'!'
	ASSIGN = r'='

	SEMI = r';'
	LPAREN =r'\('
	RPAREN = r'\)'
	LBRACE = r'{'
	RBRACE = r'}'

	NAME['const'] = CONST
	NAME['var'] = VAR
	NAME['print'] = PRINT
	NAME['break'] = BREAK
	NAME['continue'] = CONTINUE
	NAME['if'] = IF
	NAME['else'] = ELSE
	NAME['while'] = WHILE
	NAME['true'] = TRUE
	NAME['false'] = FALSE

	DOT = r'\.'
	
	# put at the bottom to avoid override single character tokens	
	@_(r"'((\\')|(\\n)|(\\x[a-fA-F0-9]{1,2})|(.))'")
	def CHAR(self, t):
		# trim the leading and trailing ' .. '
		val = t.value[1:-1]

		# check for special cases
		if val[0:2] == "\\x":
			val = chr(int(val[2:], 16))
		elif val == "\\n":
			val = "\n"
		elif val == "\'":
			val = "'"
					
		# reassign value
		t.value = val
		return t


	def error(self, t):
		print('Line %d: Bad character %r' % (self.lineno, t.value[0]))
		self.index += 1
	

# High level function that takes input source text and turns it into tokens.
# This is a natural place to use some kind of generator function.

def tokenize(text):
	lexer = WabbitLexer()
	return lexer.tokenize(text)
	

# Main program to test on input files
def main(filename):
	with open(filename) as file:
		text = file.read()

	for tok in tokenize(text):
		print(tok)

if __name__ == '__main__':
	import sys
	main(sys.argv[1])

	
			
		

			
	
