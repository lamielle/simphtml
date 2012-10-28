from tokens import TokenizeError
from parser import parse, ParseError

def isValid(lines):
	"""Returns True if the given text lines are properly formatted simple HTML, False otherwise."""
	try:
		match(parse(lines))
		return True
	except (MatchError, ParseError, TokenizeError):
		return False

class MatchError(Exception):
	"""Error class for providing line/col where match errors occur."""
	def __init__(self, reason):
		Exception.__init__(self, reason)

def match(tree):
	"""Performs a semantic analysis pass on an HtmlElem tree to determine if the
elements are properly matched.  Raises a MatchError if the open and close tags
of the given gree are not properly matched."""
	if tree.isElems():
		matchElems(tree.elems)
	elif tree.isOpenTag():
		raise MatchError("Open tag '%s' has no corresponding close tag." % tree.id)
	elif tree.isCloseTag():
		raise MatchError("Close tag '%s' has no corresponding opening tag." % tree.id)

def matchElems(elems):
	"""Match the given sequence of HtmlElem nodes."""
	# Keep track of the current open tag id
	openId = None
	for elem in elems:
		if elem.isElems():
			if openId is not None: match(elem)
			else: raise MatchError('Elems nesting found without previous open tag.')
		elif elem.isOpenTag():
			openId = elem.id
		elif elem.isCloseTag():
			if openId is None:
				raise MatchError("Close tag '%s' with no matching open tag." % elem.id)
			else:
				if openId != elem.id:
					raise MatchError("Close tag '%s' does not match open tag '%s'." % (elem.id, openId))
				openId = None
		else:
			openId = None
	if openId is not None:
		raise MatchError("Missing close tag for open tag '%s'." % openId)
