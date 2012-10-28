from tokens import TokenStream

def isValid(text):
	len(tokenize(text.split('\n'))) > 0

# Implements a DFA (state machine) that parses a sequence of lines
# and produces a token stream.
#
# Valid tokens:
# text; [^<&]*
# tag: < id > | < id />
# escape: &lt | &amp
# id: [a-zA-Z][0-9a-zA-Z\-]*


