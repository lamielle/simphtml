from unittest import TestCase
from simphtml import parse,tokenize
from simphtml.parser import *

class FileTests(TestCase):
	def test_test1(self):
		test1Ast = Elems((OpenTag('html'), Elems((Text('\nText\n'),)), CloseTag('html'), Text('\n')))
		with open('./simphtml/test/test1.html') as f:
			self.assertEqual(parse(f), test1Ast)

	def test_test2(self):
		test2Ast = Elems((OpenTag('html'), Elems((Text(' Simple\n'), StandaloneTag('standalone'), Text(' test\n'), OpenTag('a'), Elems((Text(' Blargh '), OpenTag('b'), Elems((StandaloneTag('standalone'),)), CloseTag('b'), Text('\nBoom\n'))), CloseTag('a'), Text('\n'))), CloseTag('html'), Text('\n')))
		with open('./simphtml/test/test2.html') as f:
			self.assertEqual(parse(f), test2Ast)

	def test_test3(self):
		with open('./simphtml/test/test3.html') as f:
			self.assertRaises(MatchError, parse, f)

	def test_test4(self):
		with open('./simphtml/test/test4.html') as f:
			self.assertRaises(MatchError, parse, f)

	def test_test5(self):
		with open('./simphtml/test/test5.html') as f:
			self.assertRaises(TokenizeError, parse, f)

	def test_test6(self):
		with open('./simphtml/test/test6.html') as f:
			self.assertRaises(MatchError, parse, f)

	def test_test7(self):
		with open('./simphtml/test/test7.html') as f:
			self.assertRaises(ParseError, parse, f)
