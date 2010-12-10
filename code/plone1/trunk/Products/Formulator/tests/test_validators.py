import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('Formulator')

import unittest
import xml.sax.handler
from ZPublisher.TaintedString import TaintedString
from Products.Formulator import Validator
from Products.Formulator.StandardFields import DateTimeField
from Products.Formulator.StandardFields import LinesField
from DateTime import DateTime

class TestField:
    def __init__(self, id, **kw):
        self.id = id
        self.kw = kw

    def get_value(self, name):
        # XXX hack
        return self.kw.get(name, 0)

    def get_error_message(self, key):
        return "nothing"

    def get_form_encoding(self):
        # XXX fake ... what if installed python does not support utf-8?
        return "utf-8"

class FakeSaxHandler:
    def __init__(self):
        self._xml = ''

    def startElement(self, key):
        self._xml = self._xml + '<%s>' % key
        
    def endElement(self, key):
        self._xml = self._xml + '</%s>' % key

    def characters(self, characters):
        self._xml = self._xml + characters
        
    def getXml(self):
        return self._xml
        
class FakeSaxProducer:
    def __init__(self):
        self.handler = FakeSaxHandler()

    def startElement(self, key):
        self.handler.startElement(key)

    def endElement(self, key):
        self.handler.endElement(key)

    def getXml(self):
        return self.handler.getXml()
        
class ValidatorTestCase(ZopeTestCase.ZopeTestCase):
    def assertValidatorRaises(self, exception, error_key, f, *args, **kw):
        try:
            apply(f, args, kw)
        except Validator.ValidationError, e:
            if e.error_key != error_key:
                self.fail('Got wrong error. Expected %s received %s' %
                          (error_key, e))
            else:
                return
        self.fail('Expected error %s but no error received.' % error_key)

class StringValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        self.v = Validator.StringValidatorInstance

    def tearDown(self):
        pass

    def test_basic(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0),
            'f', {'f' : 'foo'})
        self.assertEqual('foo', result)

    def test_htmlquotes(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0),
            'f', {'f' : '<html>'})
        self.assertEqual('<html>', result)

    def test_encoding(self):
        utf8_string = 'M\303\274ller' # this is a M&uuml;ller
        unicode_string = unicode(utf8_string, 'utf-8')
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=1),
            'f', {'f' : utf8_string})
        self.assertEqual(unicode_string, result)

    def test_strip_whitespace(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0),
            'f', {'f' : ' foo  '})
        self.assertEqual('foo', result)

    def test_error_too_long(self):
        self.assertValidatorRaises(
            Validator.ValidationError, 'too_long',
            self.v.validate,
            TestField('f', max_length=10, truncate=0, required=0, unicode=0),
            'f', {'f' : 'this is way too long'})

    def test_error_truncate(self):
        result = self.v.validate(
            TestField('f', max_length=10, truncate=1, required=0, unicode=0),
            'f', {'f' : 'this is way too long'})
        self.assertEqual('this is way too long'[:10], result)

    def test_error_required_not_found(self):
        # empty string
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': ''})
        # whitespace only
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': '   '})
        # not in dict
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {})

    def test_whitespace_preserve(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0,
                      whitespace_preserve=1),
            'f', {'f' : ' '})
        self.assertEqual(' ', result)

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0,
                      whitespace_preserve=0),
            'f', {'f' : ' '})
        self.assertEqual('', result)

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0,
                      whitespace_preserve=1),
            'f', {'f' : ' foo '})
        self.assertEqual(' foo ', result)

    def test_brokenTaintedString(self):
        # same as test_basic, instead that we pass in a "TaintedString"
        # this in passed by ZPublisher and looks like a string most of the time
        # but has been broken wrt. to the string.strip module in conjunction
        # with python 2.3.x. Check that we do not run into this brokeness
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=0, unicode=0),
            'f', {'f' : TaintedString('<foo>')})
        self.assertEqual('<foo>', result)
    
    def test_serializeValue(self):
        handler = FakeSaxProducer()
        string = 'This is the string value'
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.v.serializeValue(field, string, handler)
        self.assertEquals('This is the string value', handler.getXml())

    def test_deserializeValue(self):
        string = 'This is the string value'
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.assertEquals(
            'This is the string value',
            self.v.deserializeValue(field, string)
            )

    def test_serializeNonStringValues(self):
        not_a_string = 0
        handler = FakeSaxProducer()
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.v.serializeValue(field, not_a_string, handler)
        self.assertEquals('0', handler.getXml())

        
class LinesValidatorTestVase(ValidatorTestCase):

    def setUp(self):
        self.v = Validator.LinesValidatorInstance

    def test_whitespace_preserve(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': 'Two Lines \n of Text'})
        self.assertEquals(['Two Lines','of Text'], result)
        # without stripping whitespace
        result = self.v.validate(
            TestField('f', max_lenght=0, whitespace_preserve=1,
                      truncate=0, required=1, unicode=0),
            'f', {'f': 'Two Lines \n of Text'})
        self.assertEquals(['Two Lines ',' of Text'], result)

    def test_maxlength(self):
        # currently the validator checks the max lenght before stripping whitespace
        # from each line (and includes the linebreaks)
        self.assertValidatorRaises(
            Validator.ValidationError, 'too_long',
            self.v.validate,
            TestField('f', max_length=12, truncate=0, required=1, unicode=0),
            'f', {'f': 'Too long\n text'} )
        # empty lines in the middle count for "max_lines"
        self.assertValidatorRaises(
            Validator.ValidationError, 'too_many_lines',
            self.v.validate,
            TestField('f', max_lines=2, truncate=0, required=1, unicode=0),
            'f', {'f': 'Too long\n\n text'} )
        # when stripping whitespace, only leading \n will be stripped
        self.v.validate(
            TestField('f', max_lines=2, truncate=0, required=1, unicode=0),
            'f', {'f': '\nToo long\n text'} )
        # without stripping whitespace not even these will ne stripped
        self.assertValidatorRaises(
            Validator.ValidationError, 'too_many_lines',
            self.v.validate,
            TestField('f', max_lines=2, whitespace_preserve=1,
                      truncate=0, required=1, unicode=0),
            'f', {'f': '\nToo long\n text'} )
        # check max_linelength works
        self.assertValidatorRaises(
            Validator.ValidationError, 'line_too_long',
            self.v.validate,
            TestField('f', max_linelength=8, whitespace_preserve=1,
                      truncate=0, required=1, unicode=0),
            'f', {'f': '\nToo long \ntext'} )

    def test_serializeValue(self):
        handler = FakeSaxProducer()
        value = ['Two Lines ',' of Text']
        field = TestField('f', max_length=0, truncate=0, required=1, unicode=0)
        self.v.serializeValue(field, value, handler)
        self.assertEqual('Two Lines \n of Text', handler.getXml())

    def test_deserializeValue(self):
        string = 'Two Lines \n of Text'
        field = TestField('f', max_length=0, truncate=0, whitespace_preserve=1, required=0, unicode=1)
        self.assertEquals(
            ['Two Lines ', ' of Text'], 
            self.v.deserializeValue(field, string)
            )

class SelectionValidatorTestCase(ValidatorTestCase):

    def setUp(self):
        self.v = Validator.SelectionValidatorInstance

    def test_basic(self):
        result = self.v.validate(
            TestField('f', required=1, unicode=True, items=[('Some A here','a'),('Some B then','b')]),
            'f', {'f': 'b'})
        self.assertEquals('b', result)
        # with single items
        result = self.v.validate(
            TestField('f', required=1, unicode=True, items=[('ab','bb')]),
            'f', {'f': 'bb'})
        self.assertEquals('bb', result)

    def test_unicode_items(self):
        aUmlPlain='\xc3\xa4'
        aUmlUnicode=u'\xe4'
        result = self.v.validate(
            TestField('f', required=1, unicode=True, items=[(u'Some \xc3\x84 here',aUmlUnicode),(u'Some B then',u'b')]),
            'f', {'f': aUmlPlain})
        self.assertEquals(aUmlUnicode, result)


class EmailValidatorTestCase(ValidatorTestCase):

    def setUp(self):
        self.v = Validator.EmailValidatorInstance

    def test_basic(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': 'foo@bar.com'})
        self.assertEquals('foo@bar.com', result)
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': 'm.faassen@vet.uu.nl'})
        self.assertEquals('m.faassen@vet.uu.nl', result)

    def test_error_not_email(self):
        # a few wrong email addresses should raise error
        self.assertValidatorRaises(
            Validator.ValidationError, 'not_email',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': 'foo@bar.com.'})
        self.assertValidatorRaises(
            Validator.ValidationError, 'not_email',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': '@bar.com'})

    def test_error_required_not_found(self):
        # empty string
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1, unicode=0),
            'f', {'f': ''})

    def test_serializeValue(self):
        handler = FakeSaxProducer()
        string = 'eric@infrae.com'
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.v.serializeValue(TestField, string, handler)
        self.assertEqual('eric@infrae.com', handler.getXml())

    def test_deserializeValue(self):
        string = 'eric@infrae.com'
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.assertEquals(
            'eric@infrae.com', 
            self.v.deserializeValue(field, string)
            )
        
# not much for PatternValidator for now
class PatternValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        self.v = Validator.PatternValidatorInstance

    def test_ff_pattern(self):
        # test bug where an 'd','e' or 'f' in the input
        # caused garbled output for some patterns
        pattern='f-f'
        value='d-1'
        
        field= \
            TestField('f', max_length=0, truncate=0, required=1, unicode=0,
                      pattern=pattern)
        result = self.v.validate(field, 'f', {'f': value} )
        self.assertEquals(value, result)


class BooleanValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        self.v = Validator.BooleanValidatorInstance

    def tearDown(self):
        pass

    def test_basic(self):
        result = self.v.validate(
            TestField('f'),
            'f', {'f': ''})
        self.assertEquals(0, result)
        result = self.v.validate(
            TestField('f'),
            'f', {'f': 1})
        self.assertEquals(1, result)
        result = self.v.validate(
            TestField('f'),
            'f', {'f': 0})
        self.assertEquals(0, result)
        result = self.v.validate(
            TestField('f'),
            'f', {})
        self.assertEquals(0, result)

    def test_serializeValue(self):
        handler = FakeSaxProducer()
        value = False
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.v.serializeValue(field, value, handler)
        self.assertEqual('False', handler.getXml())
        handler2 = FakeSaxProducer()
        value = True
        self.v.serializeValue(field, value, handler2)
        self.assertEqual('True', handler2.getXml())

    def test_deserializeValue(self):
        string = 'False'
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.assertEquals(
            False, 
            self.v.deserializeValue(field, string)
            )
        string = 'True'
        self.assertEquals(
            True, 
            self.v.deserializeValue(field, string)
            )
        
class IntegerValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        self.v = Validator.IntegerValidatorInstance

    def test_basic(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0, start="", end=""),
            'f', {'f': '15'})
        self.assertEquals(15, result)

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0, start="", end=""),
            'f', {'f': '0'})
        self.assertEquals(0, result)

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0, start="", end=""),
            'f', {'f': '-1'})
        self.assertEquals(-1, result)

    def test_no_entry(self):
        # result should be empty string if nothing entered
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0, start="", end=""),
            'f', {'f': ''})
        self.assertEquals("", result)

    def test_ranges(self):
        # first check whether everything that should be in range is
        # in range
        for i in range(0, 100):
            result = self.v.validate(
                TestField('f', max_length=0, truncate=0, required=1,
                          start=0, end=100),
                'f', {'f': str(i)})
            self.assertEquals(i, result)
        # now check out of range errors
        self.assertValidatorRaises(
            Validator.ValidationError, 'integer_out_of_range',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start=0, end=100),
            'f', {'f': '100'})
        self.assertValidatorRaises(
            Validator.ValidationError, 'integer_out_of_range',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start=0, end=100),
            'f', {'f': '200'})
        self.assertValidatorRaises(
            Validator.ValidationError, 'integer_out_of_range',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start=0, end=100),
            'f', {'f': '-10'})
        # check some weird ranges
        self.assertValidatorRaises(
            Validator.ValidationError, 'integer_out_of_range',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start=10, end=10),
            'f', {'f': '10'})
        self.assertValidatorRaises(
            Validator.ValidationError, 'integer_out_of_range',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start=0, end=0),
            'f', {'f': '0'})
        self.assertValidatorRaises(
            Validator.ValidationError, 'integer_out_of_range',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start=0, end=-10),
            'f', {'f': '-1'})

    def test_error_not_integer(self):
        self.assertValidatorRaises(
            Validator.ValidationError, 'not_integer',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start="", end=""),
            'f', {'f': 'foo'})

        self.assertValidatorRaises(
            Validator.ValidationError, 'not_integer',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start="", end=""),
            'f', {'f': '1.0'})

        self.assertValidatorRaises(
            Validator.ValidationError, 'not_integer',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start="", end=""),
            'f', {'f': '1e'})

    def test_error_required_not_found(self):
        # empty string
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start="", end=""),
            'f', {'f': ''})
        # whitespace only
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start="", end=""),
            'f', {'f': '   '})
        # not in dict
        self.assertValidatorRaises(
            Validator.ValidationError, 'required_not_found',
            self.v.validate,
            TestField('f', max_length=0, truncate=0, required=1,
                      start="", end=""),
            'f', {})

    def test_serializeValue(self):
        handler = FakeSaxProducer()
        value = 1337
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.v.serializeValue(field, value, handler)
        self.assertEqual('1337', handler.getXml())

    def test_deserializeValue(self):
        string = '1337'
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1, start=0, end=2000)
        self.assertEquals(
            1337, 
            self.v.deserializeValue(field, string)
            )
        
class FloatValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        self.v = Validator.FloatValidatorInstance

    def test_basic(self):
        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0),
            'f', {'f': '15.5'})
        self.assertEqual(15.5, result)

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0),
            'f', {'f': '15.0'})
        self.assertEqual(15.0, result)

        result = self.v.validate(
            TestField('f', max_length=0, truncate=0,
                      required=0),
            'f', {'f': '15'})
        self.assertEqual(15.0, result)

    def test_error_not_float(self):
        self.assertValidatorRaises(
           Validator.ValidationError, 'not_float',
           self.v.validate,
           TestField('f', max_length=0, truncate=0, required=1),
           'f', {'f': '1f'})

    def test_serializeValue(self):
        handler = FakeSaxProducer()
        value = 1.00001
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.v.serializeValue(field, value, handler)
        self.assertEqual('1.00001', handler.getXml())

    def test_deserializeValue(self):
        string = '1.00001'
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1, start=0, end=2000)
        self.assertEquals(
            1.00001, 
            self.v.deserializeValue(field, string)
            )
        
class DateTimeValidatorTestCase(ValidatorTestCase):
    def setUp(self):
        self.v = Validator.DateTimeValidatorInstance

    def test_normal(self):
        result = self.v.validate(
            DateTimeField('f'),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30'})
        self.assertEquals(2002, result.year())
        self.assertEquals(12, result.month())
        self.assertEquals(1, result.day())
        self.assertEquals(10, result.hour())
        self.assertEquals(30, result.minute())

    def test_ampm(self):
        result = self.v.validate(
            DateTimeField('f', ampm_time_style=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30',
                  'subfield_f_ampm': 'am'})
        self.assertEquals(2002, result.year())
        self.assertEquals(12, result.month())
        self.assertEquals(1, result.day())
        self.assertEquals(10, result.hour())
        self.assertEquals(30, result.minute())

        result = self.v.validate(
            DateTimeField('f', ampm_time_style=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30',
                  'subfield_f_ampm': 'pm'})
        self.assertEquals(2002, result.year())
        self.assertEquals(12, result.month())
        self.assertEquals(1, result.day())
        self.assertEquals(22, result.hour())
        self.assertEquals(30, result.minute())

        self.assertValidatorRaises(
            Validator.ValidationError, 'not_datetime',
            self.v.validate,
            DateTimeField('f', ampm_time_style=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30'})

    def test_date_only(self):
        result = self.v.validate(
            DateTimeField('f', date_only=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1'})
        self.assertEquals(2002, result.year())
        self.assertEquals(12, result.month())
        self.assertEquals(1, result.day())
        self.assertEquals(0, result.hour())
        self.assertEquals(0, result.minute())

        result = self.v.validate(
            DateTimeField('f', date_only=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30'})
        self.assertEquals(2002, result.year())
        self.assertEquals(12, result.month())
        self.assertEquals(1, result.day())
        self.assertEquals(0, result.hour())
        self.assertEquals(0, result.minute())

    def test_allow_empty_time(self):
        result = self.v.validate(
            DateTimeField('f', allow_empty_time=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1'})
        self.assertEquals(2002, result.year())
        self.assertEquals(12, result.month())
        self.assertEquals(1, result.day())
        self.assertEquals(0, result.hour())
        self.assertEquals(0, result.minute())

        result = self.v.validate(
            DateTimeField('f', allow_empty_time=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30'})
        self.assertEquals(2002, result.year())
        self.assertEquals(12, result.month())
        self.assertEquals(1, result.day())
        self.assertEquals(10, result.hour())
        self.assertEquals(30, result.minute())

    def test_allow_empty_time2(self):
        result = self.v.validate(
            DateTimeField('f', allow_empty_time=1, required=0), 'f', {})
        self.assertEquals(None, result)


    def test_date_failure(self):
        self.assertValidatorRaises(
            Validator.ValidationError, 'not_datetime',
            self.v.validate,
            DateTimeField('f'),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '6',
                  'subfield_f_day': '35',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30'})

        self.assertValidatorRaises(
            Validator.ValidationError, 'not_datetime',
            self.v.validate,
            DateTimeField('f'),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '1',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '61'})

    def test_serializeValue(self):
        handler = FakeSaxProducer()
        value = self.v.validate(
            DateTimeField('f', allow_empty_time=1),
            'f', {'subfield_f_year': '2002',
                  'subfield_f_month': '12',
                  'subfield_f_day': '1',
                  'subfield_f_hour': '10',
                  'subfield_f_minute': '30'})
        field = DateTimeField('f')
        self.v.serializeValue(field, value, handler)
        date = DateTime(2002,12,01,10,30,00)
        self.assertEqual(date.HTML4(), handler.getXml())

    def test_deserializeValue(self):
        string = '2004-04-23T16:13:40Z'
        field = TestField('f', max_length=0, truncate=0, required=0, unicode=1)
        self.assertEquals(
            DateTime('2004-04-23T16:13:40Z'), 
            self.v.deserializeValue(field, string)
            )
        
def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(StringValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(LinesValidatorTestVase, 'test'))
    suite.addTest(unittest.makeSuite(SelectionValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(EmailValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(PatternValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(BooleanValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(IntegerValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(FloatValidatorTestCase, 'test'))
    suite.addTest(unittest.makeSuite(DateTimeValidatorTestCase, 'test'))

    return suite

if __name__ == '__main__':
    framework()
