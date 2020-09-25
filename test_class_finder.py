import sys
import unittest
from unittest.mock import patch, mock_open
from contextlib import contextmanager
import io

import class_finder


class TestExpandQuery(unittest.TestCase):

    @patch('class_finder.full_word_queries', [])
    def test_fullWord_query_list1(self):     
        class_finder.expand_query('Fo*Bar')     #when query has wildcard
        self.assertEqual(class_finder.full_word_queries, ['Fo*', 'Bar'])

    @patch('class_finder.full_word_queries', [])
    def test_fullWord_query_list2(self):     
        class_finder.expand_query('foobar')     #when query is completely lowercase
        self.assertEqual(class_finder.full_word_queries, [])

    @patch('class_finder.full_word_queries', [])
    def test_fullWord_query_list3(self):     
        class_finder.expand_query('FBar ')     #when query has space at the end
        self.assertEqual(class_finder.full_word_queries, ['Bar'])

    @patch('class_finder.full_word_queries', [])
    def test_fullWord_query_list4(self):     
        class_finder.expand_query('FBar')     #when query has upper & lowercase characters
        self.assertEqual(class_finder.full_word_queries, ['Bar'])

    @patch('class_finder.upper_case_query', '')
    def test_upperCase_query_string1(self):
        class_finder.expand_query('FooBarBaz')      #when query has multiple camelcase letters
        self.assertEqual(class_finder.upper_case_query, 'FBB')

    @patch('class_finder.upper_case_query', '')
    def test_upperCase_query_string2(self):
        class_finder.expand_query('B*rBaz')      #when query has wildcard character
        self.assertEqual(class_finder.upper_case_query, 'BB')

    @patch('class_finder.upper_case_query', '')
    def test_upperCase_query_string3(self):
        class_finder.expand_query('FoBa ')       #when query has space
        self.assertEqual(class_finder.upper_case_query, 'FB')

    @patch('class_finder.upper_case_query', '')
    def test_upperCase_query_string4(self):
        class_finder.expand_query('fbar')       #when query has only lowercase letters
        self.assertEqual(class_finder.upper_case_query, '')

class TestCamelCase(unittest.TestCase):

    @patch('class_finder.upper_case_query', 'FBB')
    def test_check_camelCase(self):
        self.assertTrue(class_finder.check_camel_case('FooBarBaz'))
        self.assertTrue(class_finder.check_camel_case('FooBatBuszoo'))
        self.assertFalse(class_finder.check_camel_case('BarBas'))
        self.assertFalse(class_finder.check_camel_case('MindReader'))
        self.assertFalse(class_finder.check_camel_case('a.b.FooBarbaz'))

class TestCompareWords(unittest.TestCase):

    def test_compare_words(self):
        self.assertTrue(class_finder.compare_words('FooBar', 'Foo'))
        self.assertTrue(class_finder.compare_words('operator', 'oper'))
        self.assertTrue(class_finder.compare_words('Reader', 'R*d'))
        self.assertTrue(class_finder.compare_words('Maker', '*er'))
        self.assertFalse(class_finder.compare_words('FooBar', 'Bar'))
        self.assertFalse(class_finder.compare_words('Telephone', 'phone'))

class TestCheckWordQuery(unittest.TestCase):

    def test_check_word_query(self):
        self.assertTrue(class_finder.check_word_query('FooBarBaz', ['Foo', 'Bar', 'Baz']))
        self.assertTrue(class_finder.check_word_query('ScubaArgentineOperator', ['Scuba', 'Argentine', 'Operator']))

        self.assertFalse(class_finder.check_word_query('MindReader', ['Mindreader']))
        self.assertFalse(class_finder.check_word_query('WishDreamFly', ['Fly', 'Dreaming']))


class TestLowerCasePattern(unittest.TestCase):

    def test_check_lowerCase_pattern(self):
        self.assertTrue(class_finder.check_lower_case_pattern('FooBarBaz', 'foba'))
        self.assertTrue(class_finder.check_lower_case_pattern('Bar', 'ba'))
        self.assertTrue(class_finder.check_lower_case_pattern('Thinker', 'think'))
        self.assertFalse(class_finder.check_lower_case_pattern('arBaz', 'ar'))
        self.assertFalse(class_finder.check_lower_case_pattern('baz', 'baz'))


class TestPreprocessText(unittest.TestCase):

    def test_preprocess_test(self):
        
        with self.subTest():
            text= 'c.d.FooBar   '       #when space is present in text
            actual = class_finder.preprocess_text(text)
            expected = {"class_name": 'FooBar', "text": 'c.d.FooBar'}
            self.assertEqual(actual, expected)

        with self.subTest():
            text= 'codingeek.WishMaker \n'    #when new line characted present in text
            actual = class_finder.preprocess_text(text)
            expected = {'class_name': 'WishMaker', 'text': 'codingeek.WishMaker'}
            self.assertEqual(actual, expected)

        with self.subTest():
            text=""
            actual = class_finder.preprocess_text(text)
            expected = None
            self.assertEqual(actual, expected)

        with self.subTest():
            text = 'a.b.FooBarBaz \n c.d.FooBar'
            actual = class_finder.preprocess_text(text)
            expected = None
            self.assertNotEqual(actual, expected)



def expandQuery_mock(query):
    return
class TestPrintClassList(unittest.TestCase):

    @patch('class_finder.query', 'FoBa ')
    @patch('class_finder.upper_case_query', 'FB')
    @patch('class_finder.full_word_queries', ['Fo', 'Ba'])
    @patch('class_finder.class_names', [])
    @patch('class_finder.last_word', True)
    @patch('class_finder.expand_query', expandQuery_mock)
    @patch("builtins.open", new_callable=mock_open, read_data="a.b.FooBarBaz\n c.d.FooBar\n codingeek.WishMaker\n codingeek.MindReader\n TelephoneOperator\n ScubaArgentineOperator\n YoureLeavingUsHere\n YouveComeToThisPoint\n YourEyesAreSpinningInTheirSockets")
    def test_main_function(self, mocked_open):
        class_finder.main()



    
if __name__ == '__main__':
    unittest.main()