import unittest
from simphtml import parse
from simphtml.parser import *

class TestAst(unittest.TestCase):
	def test_empty(self):
		self.assertEqual(parse(''), Elems())
		self.assertEqual(parse(' '), Elems((Text(' '),)))

	def test_text(self):
		self.assertEqual(parse('f'), Elems((Text('f'),)))
		self.assertEqual(parse('foo'), Elems((Text('foo'),)))
		self.assertEqual(parse('This is some text'), Elems((Text('This is some text'),)))
		self.assertEqual(parse('&lt'), Elems((Text('<'),)))
		self.assertEqual(parse('&amp'), Elems((Text('&'),)))
		self.assertEqual(parse('before&ampafter&ltagain'), Elems((Text('before&after<again'),)))

	def test_standalone(self):
		self.assertEqual(parse('<f/>'), Elems((StandaloneTag('f'),)))
		self.assertEqual(parse('<foo/>'), Elems((StandaloneTag('foo'),)))
		self.assertEqual(parse('<foo-bar/>'), Elems((StandaloneTag('foo-bar'),)))
		self.assertEqual(parse('<a-/>'), Elems((StandaloneTag('a-'),)))

	def test_matched(self):
		self.assertEqual(parse('<f></f>'), Elems((OpenTag('f'),CloseTag('f'))))
		self.assertEqual(parse('<foo></foo>'), Elems((OpenTag('foo'),CloseTag('foo'))))
		self.assertEqual(parse('<foo-bar></foo-bar>'), Elems((OpenTag('foo-bar'),CloseTag('foo-bar'))))

	def test_nested(self):
		self.assertEqual(parse('<f>Text</f>'), Elems((OpenTag('f'),Text('Text'),CloseTag('f'))))
		self.assertEqual(parse('<f> Text </g> Text <h>Text</h></f>'), Elems((OpenTag('f'),Text(' Text '), StandaloneTag('g'), Text(' Text ', Elems((OpenTag('h'), Text('Text'), CloseTag('f')))))))
