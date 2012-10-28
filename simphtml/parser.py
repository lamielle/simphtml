from tokens import tokenize, TokenizeError
from matcher import match, MatchError

def isValid(lines):
	"""Returns True if the given text lines are properly formatted simple HTML, False otherwise."""
	try:
		parse(lines)
		return True
	except (MatchError, ParseError, TokenizeError):
		return False

def parse(lines):
	"""Parses the given text lines and returns an AST that represents the simple
HTML document from the text.  Raises a ParseError if parsing fails.  Raises a
TokenizeError if tokenizing fails."""
	return match(SimpHtmlParser().parse(lines))

class ParseError(Exception):
	"""Error class for providing line/col where parse errors occur."""
	def __init__(self, reason, line, col):
		Exception.__init__(self, reason, line, col)
		self.reason = reason
		self.line = line
		self.col = col

class HtmlElem(object):
	"""Base HTML element class."""
	def __eq__(self, other):
		return (isinstance(other, self.__class__) and
		        self.__dict__ == other.__dict__)

	def __str__(self):
		return '%s()' % self.__class__.__name__

	def __repr__(self):
		return '%s()' % self.__class__.__name__

	def isText(self): return False
	def isOpenTag(self): return False
	def isCloseTag(self): return False
	def isElems(self): return False

class Elems(HtmlElem):
	"""Ordered sequence of HTML elements."""
	def __init__(self, elems = None):
		self.elems = elems if elems else []

	def __str__(self):
		return repr(self)

	def __repr__(self):
		return '%s(%s)' % (self.__class__.__name__, str(self.elems))

	def isElems(self): return True

class BaseTag(HtmlElem):
	"""Base class for HTML tag elements."""
	def __init__(self, id):
		self.id = id

	def __repr__(self):
		return '%s(%s)' % (self.__class__.__name__, self.id)

	def __repr__(self):
		return "%s('%s')" % (self.__class__.__name__, self.id)

class OpenTag(BaseTag):
	def isOpenTag(self): return True
class CloseTag(BaseTag):
	def isCloseTag(self): return True
class StandaloneTag(BaseTag): pass

class Text(HtmlElem):
	"""Simple text container."""
	def __init__(self, text):
		self.text = text

	def __repr__(self):
		return '%s(%s)' % (self.__class__.__name__, self.text)

	def __repr__(self):
		return "%s('%s')" % (self.__class__.__name__, self.text)

	def isText(self): return True

class SimpHtmlParser(object):
	"""Implements a DFA (state machine) that processes a token stream and produces
an AST.

The production rules for the syntax are:
<elems>      ::= <elem> <elems> | epsilon
<elem>       ::= <text> | <standalone> | <open> | <close> | <elems>
<text>       ::= [TextToken,EscapeLtToken,EscapeAmpToken]+
<standalone> ::= LtToken IdToken SlashToken GtToken
<open>       ::= LtToken IdToken GtToken
<close>      ::= LtToken SlashToken IdToken GtToken
"""
	def __init__(self):
		self.tokens = None

	def parse(self, lines):
		self.tokens = tokenize(lines, True)
		return Elems(self.elems())

	def elems(self):
		"""Produces a recursive sequence of elements."""
		elems = []
		while True:
			elem = self.elem()
			if len(elem) > 0:
				# Merge Text elements
				if len(elems) > 0 and \
				   elems[-1].isText() and \
				   len(elem) == 1 and \
				   elem[0].isText():
					elems[-1] = Text(elems[-1].text + elem[0].text)
				else:
					elems += elem
				# Close tag, bump up one level of nesting
				if elem[0].isCloseTag():
					break
			else:
				break
		return tuple(elems)

	def elem(self):
		"""Produces one or more elements."""
		try:
			token = self.tokens.next()
		except StopIteration:
			return []

		if token.isLtToken():
			return self.lt(token)
		elif token.isTextToken():
			return self.text(token)
		else:
			raise ParseError('Expected LtToken or TextToken but got %s.' %
			                 token.name(),
			                 token.line, token.col)

	def lt(self, ltToken):
		"""LtToken state handler."""
		try:
			token = self.tokens.next()
		except StopIteration:
			raise ParseError('Expected token after LtToken but ran out of tokens.', ltToken.line, ltToken.col)

		# CloseTag?
		if token.isSlashToken():
			return self.closeTag(token)
		elif token.isIdToken():
			return self.id(token)
		else:
			raise ParseError('Expected SlashToken or IdToken after LtToken but got %s.' %
			                 token.name(),
			                 token.line, token.col)

	def id(self, idToken):
		"""IdToken state handler."""
		try:
			token = self.tokens.next()
		except StopIteration:
			raise ParseError('Expected token following IdToken but ran out of tokens.', idToken.line, idToken.col)

		if token.isSlashToken():
			return self.standaloneTag(idToken)
		elif token.isGtToken():
			return self.openTag(idToken)
		else:
			raise ParseError('Expected SlashToken or GtToken after IdToken but got %s.' %
			                 token.name(),
			                 token.line, token.col)

	def openTag(self, idToken):
		"""Produces an open tag, nests the following elements, then flattens the ending tag."""
		elems = self.elems()
		if len(elems) > 1:
			return [OpenTag(idToken.id), Elems(elems[:-1]), elems[-1]]
		elif len(elems) == 1:
			return [OpenTag(idToken.id), elems[0]]
		else:
			return [OpenTag(idToken.id)]

	def standaloneTag(self, idToken):
		"""Produces a single StandaloneTag if the next token is a GtToken."""
		try:
			gtToken = self.tokens.next()
		except StopIteration:
			raise ParseError('Expected GtToken for StandaloneTag but ran out of tokens.', idToken.line, idToken.col)

		if gtToken.isGtToken():
			return [StandaloneTag(idToken.id)]
		else:
			raise ParseError('Expected GtToken for StandaloneTag but got %s.' %
			                 gtToken.name(),
			                 idToken.line, idToken.co)

	def closeTag(self, slashToken):
		"""Produces a single close tag if the next two tokens are and IdToken and a GtToken."""
		try:
			idToken = self.tokens.next()
			gtToken = self.tokens.next()
			if idToken.isIdToken() and gtToken.isGtToken():
				return [CloseTag(idToken.id)]
			else:
				raise ParseError('Expected IdToken then GtToken for CloseTag but got %s and %s.' %
				                 idToken.name(),
				                 gtToken.name(),
				                 idToken.line, idToken.col)
		except StopIteration:
			raise ParseError('Expected IdToken then GtToken for CloseTag but ran out of tokens.', slashToken.line, slashToken.col)

	def text(self, textToken):
		"""Produces a single Text element."""
		return [Text(textToken.text)]
