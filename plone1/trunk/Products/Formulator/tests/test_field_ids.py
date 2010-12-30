import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


""" random assembly testing some reported bugs.
    This is _not_ a structured or even complete test suite.
    Most tests test the "render" method of fields, thus they
    maybe could be moved to a "test_widgets" test case partially
"""

from Testing import ZopeTestCase

ZopeTestCase.installProduct('Formulator')

import unittest, re
from xml.dom.minidom import parseString
from DateTime import DateTime

from Products.Formulator.Form import ZMIForm

from Products.PythonScripts.PythonScript import PythonScript

from test_serialize import FakeRequest
from layer import FormulatorZCMLLayer

class FieldIdsTestCase(ZopeTestCase.ZopeTestCase):
    layer = FormulatorZCMLLayer
    
    def afterSetUp(self):
        self.root = self.folder
        self.root.manage_addProduct['Formulator'] \
                 .manage_add('form', 'Test Form')
        self.form = self.root.form
        self.form.manage_addProduct['Formulator']\
            .manage_addField('text','Text Field','StringField')

    def test_field_html_id(self):
        #test standard use-case
        sf = self.form.text
        self.assertEquals('field-text',sf.generate_field_html_id())
        self.assertEquals('field-text',sf.html_id)

    def test_html_id_with_field_record(self):
        #SilvaMetadata uses a 'field_record' to add uniqueness
        # to the field key, so test that as well
        sf = self.form.text
        self.assertEquals('field-text', sf.generate_field_html_id())

        sf.field_record = 'silva-extra'
        self.assertEquals('silva-extra-text-record',
                          sf.generate_field_html_id())
        
        sf.field_record = None

    def test_html_id_with_field_record(self):
        #the form name can be used to add uniqueness as well
        # to the field key, so test that as well
        sf = self.form.text
        self.assertEquals('field-text', sf.generate_field_html_id())

        self.form.name = 'test'
        self.assertEquals('testfield-text',sf.generate_field_html_id())
        self.form.name = ''

    def test_html_id_in_extra(self):
        #verify that an html id specified in the "extra" parameter
        # is used if present.  Also test the regular expression
        sf = self.form.text
        sf.values['extra'] = 'id="HTML"'
        self.assertEquals('HTML',sf.generate_field_html_id())
        sf.values['extra'] = "id='HTML'"
        self.assertEquals('HTML',sf.generate_field_html_id())
        sf.values['extra'] = 'class="blah123" id="HTML"'
        self.assertEquals('HTML',sf.generate_field_html_id())
        sf.values['extra'] = 'formid="asdf" id="HTML"'
        self.assertEquals('HTML',sf.generate_field_html_id())
        sf.values['extra'] = 'id="HTML" formid="asdf"'
        self.assertEquals('HTML',sf.generate_field_html_id())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FieldIdsTestCase))
    return suite

if __name__ == '__main__':
    framework()
