#!/usr/bin/python

#
# Parse a limited subset of html.
# Only tags with no attributes are allowed.
# Tags can be nested (<foo>..</foo>) or standalone (<foo/>)
# Tag names must be valid C identifiers (with hyphens allowed).
# Tag names are case sensitive
# Spaces are allowed in tags only between the name and the / or >
#
# The return result is an array of dictionaries.  Each dictionary
# represents either a text block, or a tag.  A tag dictionary will
# have a 'children' key iff it's not a standalone tag.
#
# For example, the following html:
#    Hi, <em>User <smiley/>!</em>
# Would be returned in the following structure:
#    [ { 'text': 'Hi, ' },
#      { 'tag': 'em',
#        'children': [
#            { 'text': 'User ' },
#            { 'tag': 'smiley' },
#            { 'text': '!' }
#         ] }
#     ]

class Error(Exception):
    def __init__(self, file_data, msg):
        Exception.__init__(self)
        self.line = file_data.get_line_num()
        self.char = file_data.get_char_pos()
        self.msg = msg

class FileData:
    """
    Class used by parser to process input data.
    Is not meant for general consumption
    """
    def __init__(self, data):
        self.data = data
        self.line = 1
        self.char = 0
        self.pos = 0

    def get_line_num(self):
        return self.line

    def get_char_pos(self):
        return self.char

    def peek(self):
        """
        Return the current char (or None if EOF) without advancing position
        """
        if self.pos == len(self.data):
            return None
        return self.data[self.pos]

    def getch(self):
        """
        Return the current char (or None if EOF)
        """
        if self.pos == len(self.data):
            return None
        ret = self.data[self.pos]
        if ret == '\n':
            self.line += 1
            self.char = 0
        else:
            self.char += 1
        self.pos += 1

        return ret

    def match(self, what):
        """
        returns True iff the string at the current position matches 'what'
        Does not handle case that 'what' contains a \n
        """
        if self.data[self.pos:self.pos+len(what)] == what:
            self.pos += len(what)
            self.char += len(what)
            return True
        return False

    def skip_space(self):
        """
        Consume any whitespace characters
        """
        c = self.peek()
        while c is not None and c.isspace():
            self.getch()
            c = self.peek()
        
    def get_id(self):
        """
        Return a string representing a valid identifier.
        Returns None if leading char is invalid.
        Leading char must be alpha or underscore.
        All subsequent chars must be alnum, underscore or hyphen.
        """
        ret = self.getch()
        if ret is None or not (ret.isalpha() or ret == '_'):
            return None
        while True:
            c = self.peek()
            if c is None or not (c.isalnum() or c == '_' or c == '-'):
                return ret
            ret += self.getch()


def parse_tag(file_data, start_tag):
    """
    Parse a block of input.  If start_tag is None, then we're parsing
    the whole file and it's OK to hit an EOF.  If start_tag is not
    None, then we're parsing the interior of that tag and we return
    iff we find a closing tag with the same name.

    The return value is an array of dictionaries, where each
    dictionary contains either a 'text' or a 'tag' key.  A dictionary
    with 'tag' will contain 'children' if it's not a standalone tag.
    """
    ret = []
    start_line = file_data.get_line_num()
    text = ''
    while True:
        c = file_data.getch()

        # Handle the case of EOF.  Valid only if we're parsing the
        # whole file.
        if c is None:
            if start_tag is not None:
                raise Error(file_data, "Failed to find closing tag for tag '%s' started at line %d" % (start_tag, start_line))

            # If we have pending text, add it to end of result
            if len(text) > 0:
                ret.append({ 'text': text })
            return ret

        # Are we starting or ending a tag?
        if c == '<':
            # Save the text we've processed so far
            if len(text) > 0:
                ret.append({ 'text' : text })
            text = ''

            # Check if we're ending a tag
            if file_data.peek() == '/':
                file_data.getch()

                end_tag = file_data.get_id()
                if end_tag is None:
                    raise Error(file_data, "Invalid closing tag: not a valid C identifier")
                file_data.skip_space()
                c = file_data.getch()
                if c != '>':
                    raise Error(file_data, "Invalid closing tag: unexpected character found before >")
                if end_tag != start_tag:
                    raise Error(file_data, "Found unexpected closing tag '%s'" % end_tag)
                return ret
                
            # We're starting a new tag, make sure it's valid
            sub_tag = file_data.get_id()
            if sub_tag is None:
                raise Error(file_data, "Invalid tag: not a valid C identifier")

            file_data.skip_space()
            c = file_data.getch()
            if c == '>':
                # It was a valid tag, go parse the interior
                children = parse_tag(file_data, sub_tag)
                ret.append({ 'tag': sub_tag, 'children': children })
            elif c == '/':
                # Looks like it's a stand-alone tag
                c = file_data.getch()
                if c != '>':
                    raise Error(file_data, "Invalid tag: / must be followed by >")
                ret.append({ 'tag': sub_tag })
            else:
                raise Error(file_data, "Invalid tag: unexpected character found before >")
        elif c == '&':
            # Look for the two valid escape sequences we handle
            if file_data.match('lt;'):
                text += '<'
            elif file_data.match('amp;'):
                text += '&'
            else:
                raise Error(file_data, "Invalid escape")
        else:
            text += c
            

def parse(file_data):
    return parse_tag(file_data, None)


if __name__ == '__main__':
    import sys
    import unittest

    if len(sys.argv) == 2:
        with open(sys.argv[1], 'r') as f:
            data = f.read()
            # Trim off trailing \n, exposes more cases to test
            if data[-1] == '\n':
                data = data[:-1]
            file_data = FileData(data)

        try:
            tree = parse(file_data)
            print tree
        except Error as e:
            print "%d(%d): %s" % (e.line, e.char, e.msg)
        sys.exit(0)
    elif len(sys.argv) != 1:
        print "Usage: %s file.html" % sys.argv[0]
        sys.exit(1)

    class TestParser(unittest.TestCase):
        def fails(self, input):
            file_data = FileData(input)
            self.assertRaises(Error, parse, file_data)

        def passes(self, input):
            file_data = FileData(input)
            parse(file_data)

        def test_1(self):
            self.fails('<')
            self.fails('<>')
            self.fails('<foo')
            self.fails('<foo>')
            self.fails('<foo></')
            self.fails('<foo></foo')
            self.fails('<foo></#foo>')
            self.passes('<foo></foo>')

            self.passes('')
            self.passes('hi')
            self.fails('&')
            self.fails('&lt')
            self.passes('&lt;')
            self.passes('&lt;;')
            self.fails('&ltt')
            self.fails('&amp')
            self.fails('&ampp')
            self.passes('&amp;')
            self.passes('&amp;;')
            self.fails('&gt;')
            self.passes('>')

            self.fails('<bar><foo></bar>')
            self.passes('<foo\n></foo>')
            self.fails('<#foo></#foo>')

            self.fails('<-foo></-foo>')
            self.passes('<_foo></_foo>')
            self.passes('<Foo></Foo>')
            self.passes('<FOO></FOO>')
            self.fails('<Foo></foo>')

            self.passes('<foo/>')
            self.passes('<foo><foo/></foo>')
            self.passes('foo <foo/> foo')
            self.passes('<foo><foo></foo></foo>')
            self.fails('<foo></foo></foo>')
            self.fails('<foo//>')

            self.passes('<foo  ></foo>')
            self.passes('<foo></foo >')
            self.passes('<foo\n/>')
            self.passes('<foo></foo\n>');

            self.fails('<0>0</0>')
            self.passes('<a0>0</a0>')
            self.fails('<foo><')
            self.passes('<a-></a->')
            self.fails('<a-></a-->')


    unittest.main()
