# This is a copy of zope.contentprovider.tales, which has been changed
# in order to fix how context and request are look up so it will work
# even if in your template you don't have the correct context (for
# instance if you use a FakeView).

import zope.component
import zope.interface
import zope.schema
import zope.event
from zope.location.interfaces import ILocation
from zope.tales import expressions
from zope.contentprovider import interfaces
from zope.contentprovider.tales import addTALNamespaceData


class ProviderExpression(expressions.StringExpr):
    """Collect content provider via a TAL namespace.

    Note that this implementation of the TALES `provider` namespace does not
    work with interdependent content providers, since each content-provider's
    stage one call is made just before the second stage is executed. If you
    want to implement interdependent content providers, you need to consider a
    TAL-independent view implementation that will complete all content
    providers' stage one before rendering any of them.
    """

    zope.interface.implements(interfaces.ITALESProviderExpression)

    def __call__(self, econtext):
        name = super(ProviderExpression, self).__call__(econtext)
        view = econtext.vars['view']
        context = view.context
        request = view.request

        # Try to look up the provider.
        provider = zope.component.queryMultiAdapter(
            (context, request, view), interfaces.IContentProvider, name)

        # Provide a useful error message, if the provider was not found.
        if provider is None:
            raise interfaces.ContentProviderLookupError(name)

        # add the __name__ attribute if it implements ILocation
        if ILocation.providedBy(provider):
            provider.__name__ = name

        # Insert the data gotten from the context
        addTALNamespaceData(provider, econtext)

        # Stage 1: Do the state update.
        zope.event.notify(interfaces.BeforeUpdateEvent(provider, request))
        provider.update()

        # Stage 2: Render the HTML content.
        return provider.render()
