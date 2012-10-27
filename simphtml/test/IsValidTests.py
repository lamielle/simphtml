import unittest
import simphtml

class TestSingleLine(unittest.TestCase):
	def test_empty(self):
		self.assertTrue(simphtml.isValid(''))

	def test_degenerate(self):
		self.assertFalse(simphtml.isValid('<'))
		self.assertFalse(simphtml.isValid('<>'))
		self.assertFalse(simphtml.isValid('>'))
		self.assertFalse(simphtml.isValid('/>'))
		self.assertFalse(simphtml.isValid('</>'))
		self.assertFalse(simphtml.isValid('<-'))
		self.assertFalse(simphtml.isValid('<->'))
		self.assertFalse(simphtml.isValid('<-/>'))
		self.assertFalse(simphtml.isValid('<1/>'))
		self.assertFalse(simphtml.isValid('<&/>'))

	def test_bad_escape(self):
		self.assertFalse(simphtml.isValid('&foo'))
		self.assertFalse(simphtml.isValid('&&'))
		self.assertFalse(simphtml.isValid('&<'))
		self.assertFalse(simphtml.isValid('&-'))
		self.assertFalse(simphtml.isValid('&1'))

	def test_text(self):
		self.assertTrue(simphtml.isValid('f'))
		self.assertTrue(simphtml.isValid('foo'))
		self.assertTrue(simphtml.isValid('This is some text'))
		self.assertTrue(simphtml.isValid('&lt'))
		self.assertTrue(simphtml.isValid('&amp'))
		self.assertTrue(simphtml.isValid('before&ampafter'))

	def test_standalone(self):
		self.assertTrue(simphtml.isValid('<f/>'))
		self.assertTrue(simphtml.isValid('<foo/>'))
		self.assertTrue(simphtml.isValid('<foo-bar/>'))
		self.assertTrue(simphtml.isValid('<a-/>'))

	def test_matched(self):
		self.assertTrue(simphtml.isValid('<f></f>'))
		self.assertTrue(simphtml.isValid('<foo></foo>'))
		self.assertTrue(simphtml.isValid('<foo-bar></foo-bar>'))


