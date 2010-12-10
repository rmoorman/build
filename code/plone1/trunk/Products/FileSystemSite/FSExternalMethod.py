from string import strip, split
from os import path, stat

import Globals
import Acquisition

from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.ExternalMethod.ExternalMethod import ExternalMethod

from utils import _dtmldir
from Permissions import ViewManagementScreens, View, FTPAccess
from DirectoryView import registerFileExtension, registerMetaType, expandpath
from FSObject import FSObject

import Permissions

## still need hookpoint for reloading metadata

class FSExternalMethod(FSObject, ExternalMethod):
    
    meta_type = 'FileSystem External Method'

    manage_options=(
        (
            {'label':'Customize', 'action':'manage_main'},
            {'label':'Test',
             'action':'',
             'help':('ExternalMethod','External-Method_Try-It.stx')},   
            )
        )

    security = ClassSecurityInfo()
    security.declareObjectProtected( Permissions.View )

    security.declareProtected( Permissions.ViewManagementScreens
                             , 'manage_main')
    manage_main = Globals.DTMLFile( 'custstx', _dtmldir )

    allowed_params = ('title', 'module', 'function')

    def _createZODBClone(self):
        """
            Create a ZODB (editable) equivalent of this object.
        """
        # XXX:  do this soon
        raise NotImplemented, "not needed yet"

    def _readFile( self, reparse ):

        fp = expandpath( self._filepath )
        file = open( fp, 'r' ) 
        parameters = {}
        
        try:
            for line in file.readlines():
                line = line.strip()
                if not line:
                    continue                    
                if line[0] == '#':
                    continue
                key, value = line.split(':')
                parameters[key.strip()] = value.strip()
                
        finally:
            file.close()

        for k in parameters.keys():
            if k not in self.allowed_params:
                del parameters[k]
        
        self.manage_edit(**parameters)

    if Globals.DevelopmentMode:
        # Provide an opportunity to update the properties.
        def __of__(self, parent):
            try:
                self = Acquisition.ImplicitAcquisitionWrapper(self, parent)
                self._updateFromFS()
                return self
            except:
                from zLOG import LOG, ERROR
                import sys
                LOG('FS Z SQL Method',
                    ERROR,
                    'Error during __of__',
                    error=sys.exc_info())
                raise

Globals.InitializeClass(FSExternalMethod)

registerFileExtension('ext', FSExternalMethod)
registerMetaType('External Method', FSExternalMethod)

