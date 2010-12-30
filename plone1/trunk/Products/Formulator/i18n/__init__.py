"""Provides a function called 'translate' that *must* be imported as '_':

    from Products.Formulator.i18n import translate as _

and will provide a MessageIDFactory that returns MessageIDs for
i18n'ing Product code and Python scripts.

Five 1.2 or later needs to be installed to make this work.
"""

try:
     #Zope since 2.10
     from zope.i18nmessageid import MessageFactory
except ImportError:
     #BBB Zope 2.9 and earlier
     from zope.i18nmessageid import MessageIDFactory as MessageFactory

translate = MessageFactory('formulator')
