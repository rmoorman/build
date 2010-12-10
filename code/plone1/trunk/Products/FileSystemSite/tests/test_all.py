import Zope
from unittest import main
from Products.FileSystemSite.tests.base.utils import build_test_suite

def test_suite():

    return build_test_suite('Products.FileSystemSite.tests',[
        'test_DirectoryView',
        'test_FSFile',
        'test_FSPythonScript',
        'test_FSPageTemplate',
        'test_FSImage',
        'test_FSSecurity',
        ])

if __name__ == '__main__':
    main(defaultTest='test_suite')
