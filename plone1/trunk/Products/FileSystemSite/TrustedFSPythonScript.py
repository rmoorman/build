# Copyright (C) 2004 by Dr. Dieter Maurer, Eichendorffstr. 23, D-66386 St. Ingbert, Germany
# see "doc/TRUSTED_LICENSE.txt" for details
#       $Id: TrustedFSPythonScript.py,v 1.2 2005/07/27 10:20:00 walco Exp $
'''FSPythonScript unrestricted by Zopes security.'''

from FSPythonScript import FSPythonScript, registerFileExtension, Cacheable

from ReuseUtils import rebindFunction
from ExtensionClassUtils import _UnCustomizable
from TrustedPythonScriptMixin import TrustedPythonScriptMixin
from TrustedPythonScript import TrustedPythonScript


class TrustedFSPythonScript(_UnCustomizable, TrustedPythonScriptMixin,
                            FSPythonScript):
  meta_type = 'Trusted Filesystem Python Script'

  _write = rebindFunction(FSPythonScript._write.im_func,
                          PythonScript=TrustedPythonScript,
                          )

registerFileExtension('xpy', TrustedFSPythonScript)
