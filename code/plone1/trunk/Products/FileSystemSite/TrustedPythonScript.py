# Copyright (C) 2004 by Dr. Dieter Maurer, Eichendorffstr. 23, D-66386 St. Ingbert, Germany
# see "doc/TRUSTED_LICENSE.txt" for details
#       $Id: TrustedPythonScript.py,v 1.1 2004/09/06 17:00:46 faassen Exp $
'''Python Script unrestricted by Zopes security.

CAUTION: Almost surely, you do not want to make this available.
'''

from Products.PythonScripts.PythonScript import PythonScript

from TrustedPythonScriptMixin import TrustedPythonScriptMixin

class TrustedPythonScript(TrustedPythonScriptMixin, PythonScript):
  '''Python Script unrestriced by Zopes security.'''
  meta_type = 'Trusted Python Script'
