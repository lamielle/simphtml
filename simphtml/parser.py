from tokens import TokenStream

def isValid(text):
	return not parse(tokens).isError()

def parse(tokens):
	return SimpHtmlParser().parse(tokens)

class HtmlElem(object):
	def __eq__(self, other):
		return (isinstance(other, self.__class__) and
		        self.__dict__ == other.__dict__)

	def isError(self): return False

class Elems(HtmlElem): pass
class OpenTag(HtmlElem): pass
class CloseTag(HtmlElem): pass
class StandaloneTag(HtmlElem): pass
class Text(HtmlElem): pass

class SimpHtmlParser(object):
	"""Implements a DFA (state machine) that processes a token stream and produces
an AST.

The production rules for the syntax is:

<elems>      ::= <elem> <elems> | epsilon
<elem>       ::= <text> | <standalone> | <open> <elems> <close>
<text>       ::= [TextToken,EscapeLtToken,EscapeAmpToken]+
<standalone> ::= LtToken IdToken SlashToken GtToken
<open>       ::= LtToken IdToken GtToken
<close>      ::= LtToken SlashToken IdToken GtToken
"""
	def __init__(self): pass

	def parse(self, tokens):
		elems = []
		return Elems()
