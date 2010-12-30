##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" CMFCore tool interfaces.

$Id: _tools.py 40047 2005-11-11 09:06:05Z yuppie $
"""

from zope.interface import Interface


class IDirectoryView(Interface):
    """ Directory views mount filesystem directories.
    """

class IFSObject(Interface):
    """An object in a directory view.
    """


class IFakeView(Interface):
    """A fake view.
    """
