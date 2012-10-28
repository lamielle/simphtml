from unittest import TestCase

import simphtml
from simphtml import tokenize
from simphtml.tokens import *

class TestEquality(TestCase):
	def test_lt(self):
		self.assertEqual(LtToken(), LtToken())
		self.assertNotEqual(LtToken(), GtToken())

	def test_slash(self):
		self.assertEqual(SlashToken(), SlashToken())
		self.assertNotEqual(SlashToken(), GtToken())

	def test_gt(self):
		self.assertEqual(GtToken(), GtToken())
		self.assertNotEqual(GtToken(), LtToken())

	def test_slash(self):
		self.assertEqual(SlashToken(), SlashToken())
		self.assertNotEqual(SlashToken(), GtToken())

	def test_escape_gt(self):
		self.assertEqual(EscapeLtToken(), EscapeLtToken())
		self.assertNotEqual(EscapeLtToken(), GtToken())

	def test_escape_amp(self):
		self.assertEqual(EscapeAmpToken(), EscapeAmpToken())
		self.assertNotEqual(EscapeAmpToken(), GtToken())

class TestSingleLineTokenStream(TestCase):
	def test_empty(self):
		self.assertEqual(tokenize(''), ())

	def test_degenerate(self):
		self.assertEqual(tokenize('<'), (LtToken(),))
		self.assertEqual(tokenize('<>'), (LtToken(), GtToken()))
		self.assertEqual(tokenize('>'), (GtToken(),))
		self.assertEqual(tokenize('/>'), (SlashToken(), GtToken()))
		self.assertEqual(tokenize('</>'), (LtToken(), SlashToken(), GtToken()))
		self.assertEqual(tokenize('<<'), (LtToken(), LtToken()))

	def test_tokenize_error(self):
		self.assertRaises(TokenizeError, tokenize, '<-')
		self.assertRaises(TokenizeError, tokenize, '<->')
		self.assertRaises(TokenizeError, tokenize, '<-/>')
		self.assertRaises(TokenizeError, tokenize, '<1/>')
		self.assertRaises(TokenizeError, tokenize, '<&/>')
		self.assertRaises(TokenizeError, tokenize, '&foo')
		self.assertRaises(TokenizeError, tokenize, '&&')
		self.assertRaises(TokenizeError, tokenize, '&<')
		self.assertRaises(TokenizeError, tokenize, '&-')
		self.assertRaises(TokenizeError, tokenize, '&1')
		self.assertRaises(TokenizeError, tokenize, '&a')
		self.assertRaises(TokenizeError, tokenize, '&am')
		self.assertRaises(TokenizeError, tokenize, '&l')

	def test_text(self):
		self.assertEqual(tokenize('f'), (TextToken('f'),))
		self.assertEqual(tokenize('foo'), (TextToken('foo'),))
		self.assertEqual(tokenize('This is some text'), (TextToken('This is some text'),))

	def test_escape(self):
		self.assertEqual(tokenize('&lt'), (EscapeLtToken(),))
		self.assertEqual(tokenize('&amp'), (EscapeAmpToken(),))
		self.assertEqual(tokenize('before&ampafter'), (TextToken('before'), EscapeAmpToken(), TextToken('after')))

	def test_standalone(self):
		self.assertEqual(tokenize('<f/>'), (LtToken(), IdToken('f'), SlashToken(), GtToken()))
		self.assertEqual(tokenize('<foo/>'), (LtToken(), IdToken('foo'), SlashToken(), GtToken()))
		self.assertEqual(tokenize('<foo-bar/>'), (LtToken(), IdToken('foo-bar'), SlashToken(), GtToken()))
		self.assertEqual(tokenize('<a-/>'), (LtToken(), IdToken('a-'), SlashToken(), GtToken()))

	def test_matched(self):
		self.assertEqual(tokenize('<f></f>'), (LtToken(), IdToken('f'), GtToken(), LtToken(), SlashToken(), IdToken('f'), GtToken()))
		self.assertEqual(tokenize('<foo></foo>'), (LtToken(), IdToken('foo'), GtToken(), LtToken(), SlashToken(), IdToken('foo'), GtToken()))
		self.assertEqual(tokenize('<foo-bar></foo-bar>'), (LtToken(), IdToken('foo-bar'), GtToken(), LtToken(), SlashToken(), IdToken('foo-bar'), GtToken()))

class TestWhiteSpaceTokenStream(TestCase):
	def test_text_with_newline(self):
		self.assertEqual(tokenize('this is some text\nwith a newline'), (TextToken('this is some text\nwith a newline'),))

	def test_escape_with_whitespace(self):
		self.assertRaises(TokenizeError, tokenize, '&a\nmp')
		self.assertRaises(TokenizeError, tokenize, '& amp')
		self.assertRaises(TokenizeError, tokenize, '&a mp')
		self.assertRaises(TokenizeError, tokenize, '&a m p')

	def test_text_whitespace(self):
		self.assertEqual(tokenize(' some text \n more text'), (TextToken(' some text \n more text'),))

	def test_tag_with_whitespace(self):
		self.assertEqual(tokenize('< foo >'), (LtToken(), IdToken('foo'), GtToken()))
		self.assertEqual(tokenize('< f >'), (LtToken(), IdToken('f'), GtToken()))
		self.assertEqual(tokenize('< / foo >'), (LtToken(), SlashToken(), IdToken('foo'), GtToken()))
		self.assertEqual(tokenize('< / f >'), (LtToken(), SlashToken(), IdToken('f'), GtToken()))
		self.assertEqual(tokenize('<  foo / >'), (LtToken(), IdToken('foo'), SlashToken(), GtToken()))
		self.assertEqual(tokenize('<  f / >'), (LtToken(), IdToken('f'), SlashToken(), GtToken()))
		self.assertEqual(tokenize('<foo / >'), (LtToken(), IdToken('foo'), SlashToken(), GtToken()))
		self.assertEqual(tokenize('<f / >'), (LtToken(), IdToken('f'), SlashToken(), GtToken()))
		self.assertEqual(tokenize('<foo/ >'), (LtToken(), IdToken('foo'), SlashToken(), GtToken()))
		self.assertEqual(tokenize('<f/ >'), (LtToken(), IdToken('f'), SlashToken(), GtToken()))
		self.assertEqual(tokenize('< foo/>'), (LtToken(), IdToken('foo'), SlashToken(), GtToken()))
		self.assertEqual(tokenize('< f/>'), (LtToken(), IdToken('f'), SlashToken(), GtToken()))
		self.assertEqual(tokenize('<\nfoo/>'), (LtToken(), IdToken('foo'), SlashToken(), GtToken()))
		self.assertEqual(tokenize('<\nfoo\n/>'), (LtToken(), IdToken('foo'), SlashToken(), GtToken()))
		self.assertEqual(tokenize('<\nfoo\n/\n>'), (LtToken(), IdToken('foo'), SlashToken(), GtToken()))

	def test_tag_with_newline(self):
		self.assertEqual(tokenize('<foo>\n</foo>'), (LtToken(), IdToken('foo'), GtToken(), TextToken('\n'), LtToken(), SlashToken(), IdToken('foo'), GtToken()))

class TestErrorPosition(TestCase):
	def test_degenerate(self):
		try: tokenize('<-')
		except TokenizeError as e:
			self.assertEqual(e.line, 0)
			self.assertEqual(e.col, 1)

		try: tokenize('<->')
		except TokenizeError as e:
			self.assertEqual(e.line, 0)
			self.assertEqual(e.col, 1)

		try: tokenize('</->')
		except TokenizeError as e:
			self.assertEqual(e.line, 0)
			self.assertEqual(e.col, 2)

		try: tokenize('&foo')
		except TokenizeError as e:
			self.assertEqual(e.line, 0)
			self.assertEqual(e.col, 1)

		try: tokenize('&foo')
		except TokenizeError as e:
			self.assertEqual(e.line, 0)
			self.assertEqual(e.col, 1)

	def test_multiline(self):
		try: tokenize('&amp\n&f\n&lt')
		except TokenizeError as e:
			self.assertEqual(e.line, 1)
			self.assertEqual(e.col, 1)

class TestTokenPos(TestCase):
	def test_simple(self):
		self.assertEqual(tokenize('<')[0].line, 0)
		self.assertEqual(tokenize('<')[0].col, 0)
		self.assertEqual(tokenize('<>')[1].line, 0)
		self.assertEqual(tokenize('<>')[1].col, 1)
		self.assertEqual(tokenize('<\n>')[1].line, 1)
		self.assertEqual(tokenize('<\n>')[1].col, 0)
