# Copyright (C) 2004 by Dr. Dieter Maurer, Eichendorffstr. 23, D-66386 St. Ingbert, Germany
# see "doc/TRUSTED_LICENSE.txt" for details
#       $Id: TrustedPythonScriptMixin.py,v 1.1 2004/09/06 17:00:46 faassen Exp $
'''Auxiliary mixin class to implement trusted PythonScripts.'''
import __builtin__
from operator import getitem

from ExtensionClass import Base
from RestrictedPython.RestrictionMutator import \
     RestrictionMutator, _print_target_name
from RestrictedPython.RCompile import RFunction, compileAndTuplize

from Products.PythonScripts.PythonScript import PythonScript

from ReuseUtils import rebindFunction


class TrustedPythonScriptMixin(Base):
  _newfun = rebindFunction(PythonScript._newfun.im_func,
                           safe_builtins=__builtin__.__dict__,
                           _getattr_=getattr,
                           _getitem_=getitem,
                           _write_=lambda ob:ob,
                           )

  def _compiler(self, *args, **kw):
    kw['globals'] = kw['globalize']
    del kw['globalize']
    gen = RFunction(*args, **kw)
    gen.rm = RestrictionMutator()
    return compileAndTuplize(gen)


class RestrictionMutator(RestrictionMutator):
  '''a 'RestrictionMutator' without restrictions.'''
  def _ok(self, *args, **kw): return 1
  checkName = checkAttrName = _ok

  def _default(self, node, walker): return walker.defaultVisitNode(node)

  visitGetattr = visitSubscript = visitAssAttr = visitExec = visitClass \
                 = visitModule = visitAugAssign = visitImport \
                 = _default

  def visitPrint(self, node, walker):
    """we add the current print target if no target is specified."""
    node = walker.defaultVisitNode(node)
    self.funcinfo._print_used = 1
    if node.dest is None: node.dest = _print_target_name
    return node

  visitPrintnl = visitPrint 
