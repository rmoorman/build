# Copyright (C) 2004 by Dr. Dieter Maurer, Eichendorffstr. 23, D-66386 St. Ingbert, Germany
# see "LICENSE.txt" for details
#       $Id: ExtensionClassUtils.py,v 1.1 2005/07/27 10:20:00 walco Exp $
'''Utilities'''

from ExtensionClass import Base

class _UnCustomizable(Base):
  '''mixin class to prevent customization.'''
  def manage_doCustomize(self):
    "do not allow customization"
    raise TypeError('This object does not support customization')
