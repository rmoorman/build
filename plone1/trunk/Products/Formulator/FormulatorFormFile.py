"""Filesystem Formulator Form module

Zope object encapsulating a Formulator Form from the filesystem,
after PageTemplateFile example.
"""

import os
from AccessControl import ClassSecurityInfo
from App.Common import package_home

from Globals import DevelopmentMode
from Globals import InitializeClass

from AccessControl import getSecurityManager
from Products.Formulator.Form import ZMIForm
from OFS.SimpleItem import Item_w__name__

class FormulatorFormFile(Item_w__name__, ZMIForm):
    meta_type = 'Formulator Form (File)'

    _v_last_read = 0

    security = ClassSecurityInfo()

    def __init__(self, filename, _prefix=None, **kw):
        if _prefix is None:
            # in Zope 2.7, could use getConfiguration()
            _prefix = SOFTWARE_HOME
        elif type(_prefix) is not type(''):
            _prefix = package_home(_prefix)
        name = kw.get('__name__')
        basepath, ext = os.path.splitext(filename)
        if name:
            self._need__name__ = 0
            self.__name__ = name
        else:
            self.__name__ = os.path.basename(basepath)
        self.filename = os.path.join(_prefix, filename)

    def _refresh_check(self):
        if self._v_last_read and not DevelopmentMode:
            return
        __traceback_info__ = self.filename
        try:
            mtime = os.path.getmtime(self.filename)
        except OSError:
            mtime = 0
        if mtime == self._v_last_read:
            return
        f = open(self.filename, "rb")
        text = f.read()
        f.close()
        # set time in advance, so no recursive reading will occur
        self._v_last_read = mtime
        self.set_xml(text)

    security.declareProtected('View management screens', 'refresh_form')
    def refresh_form(self):
        """Trigger refresh check explicitly.
        """
        self._refresh_check()
        
    security.declareProtected('View', 'has_field')
    def has_field(self, id, include_disabled):
        """Check whether the form has a field of a certain id.
        """
        self._refresh_check()
        return FormulatorFormFile.inheritedAttribute(
            'has_field')(self, id, include_disabled)

    security.declareProtected('View', 'get_field')
    def get_field(self, id, include_disabled):
        """Get a field of a certain id.
        """
        self._refresh_check()
        return FormulatorFormFile.inheritedAttribute(
            'get_field')(self, id, include_disabled)

    security.declareProtected('View', 'get_fields')    
    def get_fields(self, include_disabled=0):
        """Get all the fields for all groups (in display order).
        """
        self._refresh_check()
        return FormulatorFormFile.inheritedAttribute(
            'get_fields')(self, include_disabled)
    
    security.declareProtected('View', 'get_field_ids')
    def get_field_ids(self, include_disabled=0):
        """Get all the ids of the fields in the form.
        """
        self._refresh_check()
        return FormulatorFormFile.inheritedAttribute(
            'get_field_ids')(self, include_disabled)

    security.declareProtected('View', 'get_fields_in_group')     
    def get_fields_in_group(self, group, include_disabled=0):
        self._refresh_check()
        return FormulatorFormFile.inheritedAttribute(
            'get_fields_in_group')(self, group, include_disabled)

    security.declareProtected('View', 'get_groups')
    def get_groups(self, include_empty=0):
        """Get a list of all groups, in display order.
        """
        self._refresh_check()
        return FormulatorFormFile.inheritedAttribute(
            'get_groups')(self, include_empty)
    
    security.declareProtected('View', 'render')
    def render(self, dict=None, REQUEST=None):
        """Render form.
        """
        self._refresh_check()
        return FormulatorFormFile.inheritedAttribute(
            'render')(self, dict, REQUEST)

    security.declareProtected('View', 'render_view')
    def render_view(self, dict=None):
        """Render contents (default simplistic way).
        """
        self._refresh_check()
        return FormulatorFormFile.inheritedAttribute(
            'render_view')(self, dict)
    
    def getOwner(self, info=0):
        """Gets the owner of the executable object.

        Since this object came from the
        filesystem, it is owned by no one managed by Zope.
        """
        return None

    def __getstate__(self):
        from ZODB.POSException import StorageError
        raise StorageError, ("Instance of AntiPersistent class %s "
                             "cannot be stored." % self.__class__.__name__)

InitializeClass(FormulatorFormFile)
