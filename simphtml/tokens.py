import string
from cStringIO import StringIO

class Token(object):
	def __eq__(self, other):
		return (isinstance(other, self.__class__) and
		        self.__dict__ == other.__dict__)

	def __ne__(self, other):
		return not self.__eq__(other)

	def __str__(self):
		return '%s()' % self.__class__.__name__

	def __repr__(self):
		return '%s()' % self.__class__.__name__

class LtToken(Token): pass
class SlashToken(Token): pass
class GtToken(Token): pass
class EscapeLtToken(Token): pass
class EscapeAmpToken(Token): pass

class TextToken(Token):
	def __init__(self, text):
		self.text = text

	def __str__(self):
		return '%s(%s)' % (self.__class__.__name__, self.text)

	def __repr__(self):
		return "%s('%s')" % (self.__class__.__name__, self.text)

class IdToken(Token):
	def __init__(self, id):
		self.id = id

	def __str__(self):
		return '%s(%s)' % (self.__class__.__name__, self.id)

	def __repr__(self):
		return "%s('%s')" % (self.__class__.__name__, self.id)

class TokenizeError(Exception):
	def __init__(self):
		Exception.__init__(self)
		self.line = None
		self.col = None

	def isError(self):
		return self.line is not None and self.col is not None

# Defines constants for each token state
class TokenState(object):
	_states = (
	'START',
	'END',
	'TEXT',
	'GT',
	'LT',
	'SLASH',
	'ID_START',
	'ID_NONSTART',
	'AMP',
	'AMP_L',
	'AMP_T',
	'AMP_A',
	'AMP_M',
	'AMP_P',
	)

	@classmethod
	def initStates(cls):
		for id, state in enumerate(TokenState._states):
			setattr(cls, state, id)

# Set up the various token state constants.
TokenState.initStates()

# Produces a stream of tokens of type Token.
class TokenStream(object):
	def __init__(self, lines):
		self._lines = lines
		self._token = None
		self._prevChars = StringIO()
		self._currState = TokenState.START
		self._parseNext = {
			TokenState.START: self._start,
			TokenState.END: self._end,

			TokenState.TEXT: self._text,

			TokenState.GT: self._gt,
			TokenState.LT: self._lt,
			TokenState.SLASH: self._slash,

			TokenState.ID_START: self._idStart,
			TokenState.ID_NONSTART: self._idNonStart,

			TokenState.AMP: self._amp,
			TokenState.AMP_L: self._ampL,
			TokenState.AMP_T: self._ampT,
			TokenState.AMP_A: self._ampA,
			TokenState.AMP_M: self._ampM,
			TokenState.AMP_P: self._ampP,
		}

	def _makeTextToken(self):
		self._token = TextToken(self._prevChars.getvalue())
		self._prevChars.close()
		self._prevChars = StringIO()

	def _makeIdToken(self):
		self._token = IdToken(self._prevChars.getvalue())
		self._prevChars.close()
		self._prevChars = StringIO()

	def _start(self, char, lineNum, charPos, error):
		if char == '':
			return TokenState.END
		elif char == '<':
			return TokenState.LT
		elif char == '>':
			return TokenState.GT
		elif char == '&':
			return TokenState.AMP
		elif char == '/':
			return TokenState.SLASH
		else:
			self._prevChars.write(char)
			return TokenState.TEXT

	def _end(self, char, lineNum, charPos, error):
		return None

	def _text(self, char, lineNum, charPos, error):
		if char == '':
			self._makeTextToken()
			return TokenState.END
		elif char == '<':
			self._makeTextToken()
			return TokenState.LT
		elif char == '>':
			self._makeTextToken()
			return TokenState.GT
		elif char == '&':
			self._makeTextToken()
			return TokenState.AMP
		else:
			self._prevChars.write(char)
			return TokenState.TEXT

	def _gt(self, char, lineNum, charPos, error):
		self._token = GtToken()
		if char == '':
			return TokenState.END
		elif char == '<':
			return TokenState.LT
		elif char == '>':
			return TokenState.GT
		elif char == '&':
			return TokenState.AMP
		else:
			return TokenState.START

	def _lt(self, char, lineNum, charPos, error):
		self._token = LtToken()
		if char == '':
			return TokenState.END
		elif char == '<':
			return TokenState.LT
		elif char == '>':
			return TokenState.GT
		elif char == '&':
			return TokenState.AMP
		elif char in string.letters:
			self._prevChars.write(char)
			return TokenState.ID_START
		elif char in string.digits or char == '-':
			error.line = lineNum
			error.col = charPos
			return None
		else:
			return TokenState.START

	def _slash(self, char, lineNum, charPos, error):
		self._token = SlashToken()
		if char == '':
			return TokenState.END
		elif char == '>':
			return TokenState.GT
		elif char in string.letters:
			self._prevChars.write(char)
			return TokenState.ID_START
		else:
			return TokenState.START

	def _idStart(self, char, lineNum, charPos, error):
		if char == '':
			return TokenState.END
		elif char in string.letters or char in string.digits or char == '-':
			self._prevChars.write(char)
			return TokenState.ID_NONSTART
		else:
			self._makeIdToken()
			return TokenState.START

	def _idNonStart(self, char, lineNum, charPos, error):
		if char == '':
			self._makeIdToken()
			return TokenState.END
		elif char in string.letters or char in string.digits or char == '-':
			self._prevChars.write(char)
			return TokenState.ID_NONSTART
		else:
			self._makeIdToken()
			return TokenState.START

	def _amp(self, char, lineNum, charPos, error):
		if char == '':
			return TokenState.END
		elif char == 'l':
			return TokenState.AMP_L
		elif char == 'a':
			return TokenState.AMP_A
		else:
			error.line = lineNum
			error.col = charPos
			return None

	def _ampL(self, char, lineNum, charPos, error):
		if char == '':
			error.line = lineNum
			error.col = charPos
			return None
		elif char == 't':
			return TokenState.AMP_T
		else:
			error.line = lineNum
			error.col = charPos
			return None

	def _ampT(self, char, lineNum, charPos, error):
		self._token = EscapeLtToken()
		if char == '':
			return TokenState.END
		else:
			return TokenState.START

	def _ampA(self, char, lineNum, charPos, error):
		if char == '':
			error.line = lineNum
			error.col = charPos
			return None
		elif char == 'm':
			return TokenState.AMP_M
		else:
			error.line = lineNum
			error.col = charPos
			return None

	def _ampM(self, char, lineNum, charPos, error):
		if char == '':
			error.line = lineNum
			error.col = charPos
			return None
		elif char == 'p':
			return TokenState.AMP_P
		else:
			error.line = lineNum
			error.col = charPos
			return None

	def _ampP(self, char, lineNum, charPos, error):
		self._token = EscapeAmpToken()
		if char == '':
			return TokenState.END
		else:
			return TokenState.START

	def __iter__(self):
		return self._nextToken()

	def _nextState(self, char, lineNum, charPos, error):
		self._currState = self._parseNext[self._currState](char, lineNum, charPos, error)

	def _nextToken(self):
		error = TokenizeError()
		for lineNum, line in enumerate(self._lines):
			for charPos, char in enumerate(line):
				self._nextState(char, lineNum, charPos, error)

				# Don't eat the current char if we just moved back to the start state.
				if self._currState == TokenState.START:
					self._nextState(char, lineNum, charPos, error)

				if error.isError():
					raise error
				elif self._token is not None:
					yield self._token
					self._token = None

		# Flush the last state.
		self._nextState('', -1, -1, error)
		if error.isError():
			raise error
		elif self._token is not None:
			yield self._token
			self._token = None

	def tokens(self):
		return tuple(self)
