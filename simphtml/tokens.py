import string
import os
from cStringIO import StringIO
from types import StringType

def tokenize(lines, generator = False):
	"""Returns a sequence of simple HTML tokens for the given lines of text.  If generator is True, returns a generator instead of an explicit sequence."""
	# If lines is actually a string, tack on newlines and build an array.
	if isinstance(lines, ''.__class__):
		lines = lines.split(os.linesep)
		if len(lines) > 0:
			lastLine = lines[-1]
			lines = [line + os.linesep for line in lines[:-1]]
			lines = lines + [lastLine]
	return TokenStream(lines).tokens(generator)

class Token(object):
	"""Base class for all token types."""
	def __init__(self, line = None, col = None):
		self.line = line
		self.col = col

	def __eq__(self, other):
		return isinstance(other, self.__class__)

	def __ne__(self, other):
		return not self.__eq__(other)

	def __str__(self):
		return repr(self)

	def __repr__(self):
		return '%s()' % self.__class__.__name__

	def name(self):
		return self.__class__.__name__

	def isTextToken(self): return False
	def isLtToken(self): return False
	def isSlashToken(self): return False
	def isGtToken(self): return False
	def isIdToken(self): return False

class LtToken(Token):
	def isLtToken(self): return True
class SlashToken(Token):
	def isSlashToken(self): return True
class GtToken(Token):
	def isGtToken(self): return True

class BaseTextToken(Token):
	def isTextToken(self): return True
class EscapeLtToken(BaseTextToken):
	text = '<'
class EscapeAmpToken(BaseTextToken):
	text = '&'

class TextToken(BaseTextToken):
	"""Token type representing a block of normal text."""
	def __init__(self, text, line = None, col = None):
		Token.__init__(self, line, col)
		self.text = text

	def __eq__(self, other):
		return Token.__eq__(self,other) and self.text == other.text

	def __str__(self):
		return '%s(%s)' % (self.__class__.__name__, self.text)

	def __repr__(self):
		return "%s('%s')" % (self.__class__.__name__, self.text)

class IdToken(Token):
	"""Token type representing an identifer for a tag."""
	def __init__(self, id, line = None, col = None):
		Token.__init__(self, line, col)
		self.id = id

	def __eq__(self, other):
		return Token.__eq__(self,other) and self.id == other.id

	def __str__(self):
		return '%s(%s)' % (self.__class__.__name__, self.id)

	def __repr__(self):
		return "%s('%s')" % (self.__class__.__name__, self.id)

	def isIdToken(self): return True

class TokenizeError(Exception):
	"""Error class for providing line/col position where tokenize errors occur."""
	def __init__(self):
		Exception.__init__(self)
		self.line = None
		self.col = None

	def isError(self):
		"""Returns True if this instance represents an error, False otherwise."""
		return self.line is not None and self.col is not None

class TokenState(object):
	"""Pseudo enum class to represent the state diagram for extracting tokens."""
	_states = (
		'START',
		'END',
		'TEXT',
		'GT',
		'LT',
		'SLASH',
		'ID_START',
		'ID_NONSTART',
		'TAG_WHITE',
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

class TokenStream(object):
	"""Provides an iterable stream of tokens for the given lines of text."""
	def __init__(self, lines):
		self._lines = lines
		self._token = None
		self._prevChars = StringIO()
		self._currState = TokenState.START

		# Defines a mapping of current state to state transition handler method.
		self._parseNext = {
			TokenState.START: self._start,
			TokenState.END: self._end,

			TokenState.TEXT: self._text,

			TokenState.GT: self._gt,
			TokenState.LT: self._lt,
			TokenState.SLASH: self._slash,

			TokenState.ID_START: self._idStart,
			TokenState.ID_NONSTART: self._idNonStart,

			TokenState.TAG_WHITE: self._tagWhite,

			TokenState.AMP: self._amp,
			TokenState.AMP_L: self._ampL,
			TokenState.AMP_T: self._ampT,
			TokenState.AMP_A: self._ampA,
			TokenState.AMP_M: self._ampM,
			TokenState.AMP_P: self._ampP,
		}

	def _makeTextToken(self, lineNum, charPos):
		"""Grab the current character buffer and produce a TextToken token."""
		self._token = TextToken(self._prevChars.getvalue(), lineNum, charPos)
		self._prevChars.close()
		self._prevChars = StringIO()

	def _makeIdToken(self, lineNum, charPos):
		"""Grab the current character buffer and produce a IdToken token."""
		self._token = IdToken(self._prevChars.getvalue(), lineNum, charPos)
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
			self._makeTextToken(lineNum, charPos)
			return TokenState.END
		elif char == '<':
			self._makeTextToken(lineNum, charPos)
			return TokenState.LT
		elif char == '>':
			self._makeTextToken(lineNum, charPos)
			return TokenState.GT
		elif char == '&':
			self._makeTextToken(lineNum, charPos)
			return TokenState.AMP
		else:
			self._prevChars.write(char)
			return TokenState.TEXT

	def _gt(self, char, lineNum, charPos, error):
		self._token = GtToken(lineNum, charPos)
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
		self._token = LtToken(lineNum, charPos)
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
		elif char in string.whitespace:
			return TokenState.TAG_WHITE
		elif char in string.digits or char == '-':
			error.line = lineNum
			error.col = charPos
			return None
		else:
			return TokenState.START

	def _slash(self, char, lineNum, charPos, error):
		self._token = SlashToken(lineNum, charPos)
		if char == '':
			return TokenState.END
		elif char == '>':
			return TokenState.GT
		elif char in string.letters:
			self._prevChars.write(char)
			return TokenState.ID_START
		elif char in string.whitespace:
			return TokenState.TAG_WHITE
		else:
			return TokenState.START

	def _idStart(self, char, lineNum, charPos, error):
		if char == '':
			return TokenState.END
		elif char in string.letters or char in string.digits or char == '-':
			self._prevChars.write(char)
			return TokenState.ID_NONSTART
		elif char in string.whitespace:
			self._makeIdToken(lineNum, charPos)
			return TokenState.TAG_WHITE
		else:
			self._makeIdToken(lineNum, charPos)
			return TokenState.START

	def _idNonStart(self, char, lineNum, charPos, error):
		if char == '':
			self._makeIdToken(lineNum, charPos)
			return TokenState.END
		elif char in string.letters or char in string.digits or char == '-':
			self._prevChars.write(char)
			return TokenState.ID_NONSTART
		elif char in string.whitespace:
			self._makeIdToken(lineNum, charPos)
			return TokenState.TAG_WHITE
		else:
			self._makeIdToken(lineNum, charPos)
			return TokenState.START

	def _tagWhite(self, char, lineNum, charPos, error):
		if char == '':
			return TokenState.END
		elif char == '<':
			return TokenState.LT
		elif char == '>':
			return TokenState.GT
		elif char == '/':
			return TokenState.SLASH
		elif char in string.letters:
			self._prevChars.write(char)
			return TokenState.ID_START
		elif char in string.whitespace:
			return TokenState.TAG_WHITE
		else:
			error.line = lineNum
			error.col = charPos
			return None

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
		self._token = EscapeLtToken(lineNum, charPos)
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
		self._token = EscapeAmpToken(lineNum, charPos)
		if char == '':
			return TokenState.END
		else:
			return TokenState.START

	def __iter__(self):
		return self._nextToken()

	def _nextState(self, char, lineNum, charPos, error):
		"""Transitions from the current state to the next state."""
		self._currState = self._parseNext[self._currState](char, lineNum, charPos, error)

	def _nextToken(self):
		"""Generator method that yields a stream of tokens."""
		error = TokenizeError()
		# Predefine these so they are guaranteed to be defined after the loops.
		lineNum = -1
		charPos = -1
		for lineNum, line in enumerate(self._lines):
			for charPos, char in enumerate(line):
				self._nextState(char, lineNum, charPos, error)

				# Don't eat the current char if we just moved back to the start state.
				if self._currState == TokenState.START:
					self._nextState(char, lineNum, charPos, error)

				# Check for errors and yield the current token if one was produced.
				if error.isError():
					raise error
				elif self._token is not None:
					yield self._token
					self._token = None

		# Flush the last state.
		self._nextState('', lineNum, charPos, error)
		if error.isError():
			raise error
		elif self._token is not None:
			yield self._token
			self._token = None

	def tokens(self, generator = False):
		"""Returns a tuple of tokens for this TokenStream."""
		if generator:
			return (token for token in self)
		else:
			return tuple(self)
