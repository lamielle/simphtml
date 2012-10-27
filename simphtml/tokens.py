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
		self._prevState = None
		self._currState = TokenState.TEXT
		self._parseNext = {
			TokenState.TEXT: self.text,

			TokenState.GT: self.gt,
			TokenState.LT: self.lt,
			TokenState.SLASH: self.slash,

			TokenState.ID_START: self.idStart,
			TokenState.ID_NONSTART: self.idNonStart,

			TokenState.AMP: self.amp,
			TokenState.AMP_L: self.ampL,
			TokenState.AMP_T: self.ampT,
			TokenState.AMP_A: self.ampA,
			TokenState.AMP_M: self.ampM,
			TokenState.AMP_P: self.ampP,
		}

	def text(self, char, lineNum, charPos, error):
		self._token = TextToken(char)
		return TokenState.TEXT

	def gt(self, char, lineNum, charPos, error): pass
	def lt(self, char, lineNum, charPos, error): pass
	def slash(self, char, lineNum, charPos, error): pass
	def idStart(self, char, lineNum, charPos, error): pass
	def idNonStart(self, char, lineNum, charPos, error): pass
	def amp(self, char, lineNum, charPos, error): pass
	def ampL(self, char, lineNum, charPos, error): pass
	def ampT(self, char, lineNum, charPos, error): pass
	def ampA(self, char, lineNum, charPos, error): pass
	def ampM(self, char, lineNum, charPos, error): pass
	def ampP(self, char, lineNum, charPos, error): pass

	def __iter__(self):
		return self._nextToken()

	def _nextToken(self):
		error = TokenizeError()
		for lineNum, line in enumerate(self._lines):
			for charPos, char in enumerate(line):
				self._prevState = self._currState
				self._currState = self._parseNext[self._prevState](char, lineNum, charPos, error)
				if error.isError():
					raise error
				elif self._token is not None:
					yield self._token
					self._token = None

	def tokens(self):
		return tuple(self)
