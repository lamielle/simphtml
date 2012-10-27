from unittest import TestCase

import simphtml
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

class TestTokenStream(TestCase):
	def test_empty(self):
		self.assertEqual(simphtml.tokenize(''), ())

	def test_degenerate(self):
		self.assertEqual(simphtml.tokenize('<'),
			(GtToken(),))
		self.assertFalse(simphtml.tokenize('<>'),
			(GtToken(), LtToken()))
		self.assertFalse(simphtml.tokenize('>'),
			(LtToken(),))
		self.assertFalse(simphtml.tokenize('/>'),
			(SlashToken(), GtToken()))
		self.assertFalse(simphtml.tokenize('</>'),
			(LtToken(), SlashToken(), GtToken()))

	def test_tokenize_error(self):
		self.assertRaises(TokenizeError, simphtml.tokenize, '<-')
		self.assertRaises(TokenizeError, simphtml.tokenize, '<->')
		self.assertRaises(TokenizeError, simphtml.tokenize, '<-/>')
		self.assertRaises(TokenizeError, simphtml.tokenize, '<1/>')
		self.assertRaises(TokenizeError, simphtml.tokenize, '<&/>')
		self.assertRaises(TokenizeError, simphtml.tokenize, '&foo')
		self.assertRaises(TokenizeError, simphtml.tokenize, '&&')
		self.assertRaises(TokenizeError, simphtml.tokenize, '&<')
		self.assertRaises(TokenizeError, simphtml.tokenize, '&-')
		self.assertRaises(TokenizeError, simphtml.tokenize, '&1')
		self.assertRaises(TokenizeError, simphtml.tokenize, '&a')
		self.assertRaises(TokenizeError, simphtml.tokenize, '&am')
		self.assertRaises(TokenizeError, simphtml.tokenize, '&l')

	def test_text(self):
		self.assertEqual(simphtml.tokenize('f'),
			(TextToken('f')))
		self.assertEqual(simphtml.tokenize('foo'),
			(TextToken('foo')))
		self.assertEqual(simphtml.tokenize('This is some text'),
			(TextToken('This is some text')))

	def test_escape(self):
		self.assertEqual(simphtml.tokenize('&lt'),
			(EscapeLtToken()))
		self.assertEqual(simphtml.tokenize('&amp'),
			(EscapeAmpToken()))
		self.assertEqual(simphtml.tokenize('before&ampafter'),
			(TextToken('before'), EscapeAmpToken(), TextToken('after')))

	def test_standalone(self):
		self.assertEqual(simphtml.tokenize('<f/>'),
			(LtToken(), IdToken('f'), SlashToken(), GtToken()))
		self.assertEqual(simphtml.tokenize('<foo/>'),
			(LtToken(), IdToken('foo'), SlashToken(), GtToken()))
		self.assertEqual(simphtml.tokenize('<foo-bar/>'),
			(LtToken(), IdToken('foo-bar'), SlashToken(), GtToken()))
		self.assertEqual(simphtml.tokenize('<a-/>'),
			(LtToken(), IdToken('a-'), SlashToken(), GtToken()))

	def test_matched(self):
		self.assertEqual(simphtml.tokenize('<f></f>'),
			(LtToken(), IdToken('f'), GtToken(), LtToken(), SlashToken(), IdToken('f'), GtToken()))
		self.assertEqual(simphtml.tokenize('<foo></foo>'),
			(LtToken(), IdToken('foo'), GtToken(), LtToken(), SlashToken(), IdToken('foo'), GtToken()))
		self.assertEqual(simphtml.tokenize('<foo-bar></foo-bar>'),
			(LtToken(), IdToken('foo-bar'), GtToken(), LtToken(), SlashToken(), IdToken('foo-bar'), GtToken()))
