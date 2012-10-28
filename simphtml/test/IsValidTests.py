from unittest import TestCase
from simphtml import isValid

class TestSingleLine(TestCase):
	def test_empty(self):
		self.assertTrue(isValid(''))

	def test_degenerate(self):
		self.assertFalse(isValid('<'))
		self.assertFalse(isValid('<>'))
		self.assertFalse(isValid('>'))
		self.assertFalse(isValid('/>'))
		self.assertFalse(isValid('</>'))
		self.assertFalse(isValid('<-'))
		self.assertFalse(isValid('<->'))
		self.assertFalse(isValid('<-/>'))
		self.assertFalse(isValid('<1/>'))
		self.assertFalse(isValid('<&/>'))

	def test_bad_escape(self):
		self.assertFalse(isValid('&foo'))
		self.assertFalse(isValid('&&'))
		self.assertFalse(isValid('&<'))
		self.assertFalse(isValid('&-'))
		self.assertFalse(isValid('&1'))

	def test_text(self):
		self.assertTrue(isValid('f'))
		self.assertTrue(isValid('foo'))
		self.assertTrue(isValid('This is some text'))
		self.assertTrue(isValid('&lt'))
		self.assertTrue(isValid('&amp'))
		self.assertTrue(isValid('before&ampafter'))

	def test_standalone(self):
		self.assertTrue(isValid('<f/>'))
		self.assertTrue(isValid('<foo/>'))
		self.assertTrue(isValid('<foo-bar/>'))
		self.assertTrue(isValid('<a-/>'))

	def test_matched(self):
		self.assertTrue(isValid('<f></f>'))
		self.assertTrue(isValid('<foo></foo>'))
		self.assertTrue(isValid('<foo-bar></foo-bar>'))

	def test_unmatched(self):
		self.assertFalse(isValid('<bar>'))
		self.assertFalse(isValid('</bar>'))
		self.assertFalse(isValid('<f></g>'))
		self.assertFalse(isValid('<f><f><g></f>'))
		self.assertFalse(isValid('<f><g></f></g>'))
