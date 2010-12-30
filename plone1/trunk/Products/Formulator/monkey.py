from AccessControl import allow_class, allow_module

def monkey_zope3_message_id():
    try:
        #BBB Zope 2.9 and earlier
        from zope.i18nmessageid.messageid import MessageID
        # open it up for Zope 2...
        allow_class(MessageID)
    except ImportError:
        # Zope since 2.10: we dont have to allow "Message", it seems
        from zope.i18nmessageid.message import Message
        # allow_class(Message)
        # instead we have to allow the module ...
        allow_module('zope.i18nmessageid.message')

def patch_all():
    monkey_zope3_message_id()
    
