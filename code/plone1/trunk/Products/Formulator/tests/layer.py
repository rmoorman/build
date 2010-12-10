from zope.testing.cleanup import cleanUp as _cleanUp

def setDebugMode(mode):
    import Products.Five.fiveconfigure as fc
    fc.debug_mode = mode
    
def cleanUp():
    """Clean up component architecture."""
    _cleanUp()
    import Products.Five.zcml as zcml
    zcml._initialized = 0
    
class FormulatorZCMLLayer:
    @classmethod
    def setUp(cls):
        cleanUp()
        setDebugMode(1)
        import Products.Five.zcml as zcml
        zcml.load_site()
        setDebugMode(0)

    @classmethod
    def tearDown(cls):
        cleanUp()
