##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Portal services base objects

$Id: __init__.py 40391 2005-11-28 16:21:21Z yuppie $
"""


from Products.FileSystemSite import DirectoryView, FSImage, FSFile, FSPropertiesObject
from Products.FileSystemSite import FSDTMLMethod, FSPythonScript, FSPageTemplate
from Products.FileSystemSite import utils

try:
    from Products import ZSQLMethods
    from Products.FileSystemSite import FSZSQLMethod
    HAVE_SQL_METHODS = True
except ImportError:
    HAVE_SQL_METHODS = False

def initialize(context):

    context.registerClass(
        DirectoryView.DirectoryView,
        constructors=(('manage_addDirectoryViewForm',
                       DirectoryView.manage_addDirectoryViewForm),
                      DirectoryView.manage_addDirectoryView,
                      DirectoryView.manage_listAvailableDirectories,
                      ),
        icon='images/dirview.gif'
        )

utils.registerIcon(FSDTMLMethod.FSDTMLMethod,
                   'images/fsdtml.gif', globals())
utils.registerIcon(FSPythonScript.FSPythonScript,
                   'images/fspy.gif', globals())
utils.registerIcon(FSImage.FSImage,
                   'images/fsimage.gif', globals())
utils.registerIcon(FSFile.FSFile,
                   'images/fsfile.gif', globals())
utils.registerIcon(FSPageTemplate.FSPageTemplate,
                   'images/fspt.gif', globals())
utils.registerIcon(FSPropertiesObject.FSPropertiesObject,
                   'images/fsprops.gif', globals())
if HAVE_SQL_METHODS:
    utils.registerIcon(FSZSQLMethod.FSZSQLMethod,
                       'images/fssqlmethod.gif', globals())
