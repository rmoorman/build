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
""" Customizable Python scripts that come from the filesystem.

$Id: FSPythonScript.py 41760 2006-02-23 14:02:19Z mj $
"""

import new

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from ComputedAttribute import ComputedAttribute
from App.special_dtml import DTMLFile
from App.class_init import InitializeClass
from OFS.Cache import Cacheable
from Products.PythonScripts.PythonScript import PythonScript
from Shared.DC.Scripts.Script import Script

from DirectoryView import registerFileExtension
from DirectoryView import registerMetaType
from FSObject import FSObject
from Permissions import FTPAccess
from Permissions import View
from Permissions import ViewManagementScreens
from utils import _dtmldir
from utils import expandpath

_marker = []


class FSPythonScript (FSObject, Script):
    """FSPythonScripts act like Python Scripts but are not directly
    modifiable from the management interface."""

    meta_type = 'Filesystem Script (Python)'
    _params = _body = ''
    _proxy_roles = ()

    _owner = None  # Unowned

    manage_options=(
        (
            {'label':'Customize', 'action':'manage_main'},
            {'label':'Test',
             'action':'ZScriptHTML_tryForm',
             'help': ('PythonScripts', 'PythonScript_test.stx')},
            )
            + Cacheable.manage_options
        )

    # Use declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(View)
    security.declareProtected(View, 'index_html',)
    # Prevent the bindings from being edited TTW
    security.declarePrivate('ZBindings_edit','ZBindingsHTML_editForm',
                            'ZBindingsHTML_editAction')

    security.declareProtected(ViewManagementScreens, 'manage_main')
    manage_main = DTMLFile('custpy', _dtmldir)

    def _createZODBClone(self):
        """Create a ZODB (editable) equivalent of this object."""
        obj = PythonScript(self.getId())
        obj.write(self.read())
        return obj

    def _readFile(self, reparse):
        """Read the data from the filesystem.

        Read the file (indicated by exandpath(self._filepath), and parse the
        data if necessary.
        """
        fp = expandpath(self._filepath)
        file = open(fp, 'rU')
        try: data = file.read()
        finally: file.close()
        if reparse:
            self._write(data, reparse)

    def _validateProxy(self, roles=None):
        pass

    def __render_with_namespace__(self, namespace):
        '''Calls the script.'''
        self._updateFromFS()
        return Script.__render_with_namespace__(self, namespace)

    def __call__(self, *args, **kw):
        '''Calls the script.'''
        self._updateFromFS()
        return Script.__call__(self, *args, **kw)

    _exec = PythonScript._exec.im_func

    security.declareProtected(ViewManagementScreens, 'getModTime')
    # getModTime defined in FSObject

    security.declareProtected(ViewManagementScreens, 'ZScriptHTML_tryForm')
    # ZScriptHTML_tryForm defined in Shared.DC.Scripts.Script.Script

    def ZScriptHTML_tryParams(self):
        """Parameters to test the script with."""
        param_names = []
        for name in self._params.split(','):
            name = name.strip()
            if name and name[0] != '*':
                param_names.append( name.split('=', 1)[0] )
        return param_names

    security.declareProtected(ViewManagementScreens, 'read')
    def read(self):
        self._updateFromFS()
        return self._source

    security.declareProtected(ViewManagementScreens, 'document_src')
    def document_src(self, REQUEST=None, RESPONSE=None):
        """Return unprocessed document source."""

        if RESPONSE is not None:
            RESPONSE.setHeader('Content-Type', 'text/plain')
        return self._source

    security.declareProtected(ViewManagementScreens, 'PrincipiaSearchSource')
    def PrincipiaSearchSource(self):
        "Support for searching - the document's contents are searched."
        return "%s\n%s" % (self._params, self._body)

    security.declareProtected(ViewManagementScreens, 'params')
    def params(self): return self._params

    security.declareProtected(ViewManagementScreens, 'manage_haveProxy')
    manage_haveProxy = PythonScript.manage_haveProxy.im_func

    security.declareProtected(ViewManagementScreens, 'body')
    def body(self): return self._body

    security.declareProtected(ViewManagementScreens, 'get_size')
    def get_size(self): return len(self.read())

    security.declareProtected(FTPAccess, 'manage_FTPget')
    def manage_FTPget(self):
        "Get source for FTP download"
        self.REQUEST.RESPONSE.setHeader('Content-Type', 'text/plain')
        return self.read()

    def _write(self, text, compile):
        '''
        Parses the source, storing the body, params, title, bindings,
        and source in self.  If compile is set, compiles the
        function.
        '''
        ps = PythonScript(self.id)
        ps.write(text)
        if compile:
            ps._makeFunction()
            self._v_ft = ps._v_ft
            self.func_code = ps.func_code
            self.func_defaults = ps.func_defaults
        self._body = ps._body
        self._params = ps._params
        self.title = ps.title
        self._setupBindings(ps.getBindingAssignments().getAssignedNames())
        self._source = ps.read()  # Find out what the script sees.

    def func_defaults(self):
        # This ensures func_code and func_defaults are
        # set when the code hasn't been compiled yet,
        # just in time for mapply().  Truly odd, but so is mapply(). :P
        self._updateFromFS()
        return self.__dict__.get('func_defaults', None)
    func_defaults = ComputedAttribute(func_defaults, 1)

    def func_code(self):
        # See func_defaults.
        self._updateFromFS()
        return self.__dict__.get('func_code', None)
    func_code = ComputedAttribute(func_code, 1)

    def title(self):
        # See func_defaults.
        self._updateFromFS()
        return self.__dict__.get('title', None)
    title = ComputedAttribute(title, 1)

    def getBindingAssignments(self):
        # Override of the version in Bindings.py.
        # This version ensures that bindings get loaded on demand.
        if not hasattr(self, '_bind_names'):
            # Set a default first to avoid recursion
            self._setupBindings()
            # Now do it for real
            self._updateFromFS()
        return self._bind_names

InitializeClass(FSPythonScript)


class FSPythonScriptTracebackSupplement:
    """Implementation of ITracebackSupplement

    Makes script-specific info available in exception tracebacks.
    """
    def __init__(self, script, line=-1):
        self.object = script
        # If line is set to -1, it means to use tb_lineno.
        self.line = line


registerFileExtension('py', FSPythonScript)
registerMetaType('Script (Python)', FSPythonScript)
