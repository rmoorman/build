from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.utils import _checkPermission, _getAuthenticatedUser
from Products.CMFCore.utils import getToolByName, _dtmldir
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions as CMFCorePermissions
from Products.CMFCore.interfaces.DublinCore import DublinCore
from types import TupleType, UnicodeType
from urllib import urlencode
import urlparse
from cgi import parse_qs

import re
import sys
import traceback

from types import TupleType, UnicodeType, DictType, StringType

from zLOG import LOG, INFO, WARNING

def log(summary='', text='', log_level=INFO):
    LOG('Plone Debug', log_level, summary, text)

try:
    True
except:
    True=1
    False=0    
    
EMAIL_RE = re.compile(r"^([0-9a-zA-Z_&.+-]+!)*[0-9a-zA-Z_&.+-]+@(([0-9a-z]([0-9a-z-]*[0-9a-z])?\.)+[a-z]{2,6}|([0-9]{1,3}\.){3}[0-9]{1,3})$")
EMAIL_CUTOFF_RE = re.compile(r".*[\n\r][\n\r]") # used to find double new line (in any variant)

#XXX Remove this when we don't depend on python2.1 any longer, use email.Utils.getaddresses instead
from rfc822 import AddressList
def _getaddresses(fieldvalues):
    """Return a list of (REALNAME, EMAIL) for each fieldvalue."""
    all = ', '.join(fieldvalues)
    a = AddressList(all)
    return a.addresslist    
    
class PloneTool (UniqueObject, SimpleItem):
    id = 'plone_utils'
    meta_type= 'Plone Utility Tool'
    security = ClassSecurityInfo()
    plone_tool = 1
    field_prefix = 'field_' # Formulator prefixes for forms

    def _safeSendTo(self, body, mto, mfrom):
        # this function is private in Plone and should be
        # the function used for sending
        # email. It does the following:
        #    
        #  - ensures that anything being sent through is only
        #    sent to the emails specified and not headers in the
        #    email
        #
        #  - ensure that from and to are only one, and only one email
        if not self.validateSingleEmailAddress(mfrom):
            raise ValueError, 'The "from" email address did not validate'
        
        if not self.validateEmailAddresses(mto):
            raise ValueError, 'The "to" email address did not validate'
        
        host = self.MailHost
        host.send(body, mto, mfrom)

    security.declarePublic('sendto')
    def sendto( self, variables = {} ):
        """Sends a link of a page to someone
        """
        if not variables: return

        # the subject is in the header, so must be checked
        if variables['title'].find('\n') >= 0:
            raise ValueError, 'That title contains a new line, which is illegal'

        mail_text = self.sendto_template(self
                                         , send_from_address = variables['send_from_address']
                                         , send_to_address = variables['send_to_address']
                                         , url = variables['url']
                                         , title = variables['title']
                                         , description = variables['description']
                                         , comment = variables['comment'])

        # the template is built with send_to and send_from
        # but we know _safeSendTo will check them as well
        # so we should be ok
        self._safeSendTo(mail_text, 
            variables['send_to_address'], 
            variables['send_from_address'])

    security.declarePublic('validateSingleNormalizedEmailAddress')
    def validateSingleNormalizedEmailAddress(self, address):
        """Lower-level function to validate a single normalized email address, see validateEmailAddress
        """
        if type(address) is not StringType:
            return False

        sub = EMAIL_CUTOFF_RE.match(address);
        if sub != None:
            # Address contains two newlines (possible spammer relay attack)
            return False

        # sub is an empty string if the address is valid
        sub = EMAIL_RE.sub('', address)
        if sub == '':
            return True
        return False

    security.declarePublic('validateSingleEmailAddress')
    def validateSingleEmailAddress(self, address):
        """Validate a single email address, see also validateEmailAddresses
        """
        if type(address) is not StringType:
            return False
        
        sub = EMAIL_CUTOFF_RE.match(address);
        if sub != None:
            # Address contains two newlines (spammer attack using "address\n\nSpam message")
            return False
        
        if len(_getaddresses([address])) != 1:
            # none or more than one address
            return False
        
        # Validate the address
        for name,addr in _getaddresses([address]):
            if not self.validateSingleNormalizedEmailAddress(addr):
                return False
        return True

    security.declarePublic('validateEmailAddresses')
    def validateEmailAddresses(self, addresses):
        """Validate a list of possibly several email addresses, see also validateSingleEmailAddress
        """
        if type(addresses) is not StringType:
            return False
        
        sub = EMAIL_CUTOFF_RE.match(addresses);
        if sub != None:
            # Addresses contains two newlines (spammer attack using "To: list\n\nSpam message")
            return False
        
        # Validate each address
        for name,addr in _getaddresses([addresses]):
            if not self.validateSingleNormalizedEmailAddress(addr):
                return False
        return True            
                    
    security.declarePublic('editMetadata')
    def editMetadata( self
                     , obj
                     , allowDiscussion=None
                     , title=None
                     , subject=None
                     , description=None
                     , contributors=None
                     , effective_date=None
                     , expiration_date=None
                     , format=None
                     , language=None
                     , rights=None
                     ,  **kwargs):
        """ responsible for setting metadata on a content object 
            we assume the obj implemented IDublinCoreMetadata 
        """
        REQUEST=self.REQUEST
        pfx=self.field_prefix
        def tuplify( value ):
            if not type(value) is TupleType:
                value = tuple( value )
            temp = filter( None, value )
            return tuple( temp )
        if title is None:
            title=REQUEST.get(pfx+'title', obj.Title())
        if subject is None:
            subject=REQUEST.get(pfx+'subject', obj.Subject())
        if description is None:
            description=REQUEST.get(pfx+'description', obj.Description())
        if contributors is None:
            contributors=tuplify(REQUEST.get(pfx+'contributors', obj.Contributors()))
        else:    
            contributors=tuplify(contributors)
        if effective_date is None:
            effective_date=REQUEST.get(pfx+'effective_date', obj.EffectiveDate())
        if effective_date == '':
            effective_date = 'None'
        if expiration_date is None:
            expiration_date=REQUEST.get(pfx+'expiration_date', obj.ExpirationDate())
        if expiration_date == '':
            expiration_date = 'None'
        if format is None:
            format=REQUEST.get('text_format', obj.Format())
        if language is None:
            language=REQUEST.get(pfx+'language', obj.Language())
        if rights is None:
            rights=REQUEST.get(pfx+'rights', obj.Rights())
        if allowDiscussion and hasattr(allowDiscussion, 'lower'):
            allowDiscussion=allowDiscussion.lower().strip()
            if allowDiscussion=='default': allowDiscussion=None
            elif allowDiscussion=='off': allowDiscussion=0
            elif allowDiscussion=='on': allowDiscussion=1
            getToolByName(self, 'portal_discussion').overrideDiscussionFor(obj, allowDiscussion)
            
        obj.editMetadata( title=title
                        , description=description
                        , subject=subject
                        , contributors=contributors
                        , effective_date=effective_date
                        , expiration_date=expiration_date
                        , format=format
                        , language=language
                        , rights=rights )

    def _renameObject(self, obj, id):
        if not id:
            REQUEST=self.REQUEST
            id = REQUEST.get('id', '')
            id = REQUEST.get(self.field_prefix+'id', '')
        if id != obj.getId():
            try:
                obj.getParentNode().manage_renameObject(obj.getId(), id)
            except: #XXX have to do this for Topics and maybe other folderish objects
                obj.aq_parent.manage_renameObject(obj.getId(), id)

    def _makeTransactionNote(self, obj, msg=''):
        #XXX why not aq_parent()?
        relative_path='/'.join(getToolByName(self, 'portal_url').getRelativeContentPath(obj)[:-1])
        if not msg:
            msg=relative_path+'/'+obj.title_or_id()+' has been modified.'
        if isinstance(msg, UnicodeType):
            # Convert unicode to a regular string for the backend write IO.
            # UTF-8 is the only reasonable choice, as using unicode means
            # that Latin-1 is probably not enough.
            msg = msg.encode('utf-8')
        get_transaction().note(msg)

    security.declarePublic('contentEdit')
    def contentEdit(self, obj, **kwargs):
        """ encapsulates how the editing of content occurs """

        #XXX Interface package appears to be broken.  Atleast for Forum objects.
        #    it may blow up on things that *done* implement the DublinCore interface. 
        #    Someone please look into this.  We should probably catch the exception (think its Tuple error)
        #    instead of swallowing all exceptions.
        try:
            if DublinCore.isImplementedBy(obj):
                apply(self.editMetadata, (obj,), kwargs)
        except: 
            pass
        
        if kwargs.get('id', None) is not None: 
            self._renameObject(obj, id=kwargs['id'].strip()) 
	
        self._makeTransactionNote(obj) #automated the manual transaction noting in xxxx_edit.py

    security.declarePublic('availableMIMETypes')
    def availableMIMETypes(self):
        """ Return a map of mimetypes """
        # This should probably be done in a more efficent way.
        import mimetypes
        
        result = []
        for mimetype in mimetypes.types_map.values():
            if not mimetype in result:
                result.append(mimetype)

        result.sort()
        return result

    security.declareProtected(CMFCorePermissions.View, 'getWorkflowChainFor')
    def getWorkflowChainFor(self, object):
        """ Proxy the request for the chain to the workflow
            tool, as this method is private there.
        """
        wftool = getToolByName(self, 'portal_workflow')
        wfs=()
        try:
            wfs=wftool.getChainFor(object)
        except: #XXX ick
            pass 
        return wfs

    security.declareProtected(CMFCorePermissions.View, 'getReviewStateTitleFor')
    def getReviewStateTitleFor(self, obj):
        """Utility method that gets the workflow state title for the object's review_state.
           Returns None if no review_state found.
           """
        wf_tool=getToolByName(self, 'portal_workflow')
        wfs=()
        review_states=()
        objstate=None
        try:
            objstate=wf_tool.getInfoFor(obj, 'review_state')
            wfs=wf_tool.getWorkflowsFor(obj)
        except WorkflowException, e:
            pass
        if wfs:
            for w in wfs:
                if w.states.has_key(objstate):
                    return w.states[objstate].title
        return None

    # Convenience method since skinstool requires loads of acrobatics.
    # We use this for the reconfig form
    security.declareProtected(CMFCorePermissions.ManagePortal, 'setDefaultSkin')
    def setDefaultSkin(self, default_skin):
        """ sets the default skin """
        st=getToolByName(self, 'portal_skins')
        st.default_skin=default_skin        

    # Set the skin on the page to the specified value
    # Can be called from a page template, but it must be called before
    # anything anything on the skin path is resolved (e.g. main_template).
    # XXX Note: This method will eventually be replaced by the setCurrentSkin
    # method that is slated for CMF 1.4
    security.declarePublic('setCurrentSkin')
    def setCurrentSkin(self, skin_name):
        """ sets the current skin """
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal._v_skindata=(self.REQUEST, self.getSkinByName(skin_name), {} )
     
    #XXX deprecated methods
    security.declarePublic('getNextPageFor')
    def getNextPageFor(self, context, action, status, **kwargs):
        log( 'Plone Tool Deprecation', action + ' has called plone_utils.getNextPageFor()'    
           + ' which has been deprecated use portal_navigation.getNextRequestFor() instead.'
           , WARNING)
        
        nav_tool=getToolByName(self, 'portal_navigation')
        return nav_tool.getNextPageFor(context, action, status, **kwargs)
            
    security.declarePublic('getNextRequestFor')
    def getNextRequestFor(self, context, action, status, **kwargs):
        log( 'Plone Tool Deprecation', action + ' has called plone_utils.getNextPageFor()' 
           + ' which has been deprecated use portal_navigation.getNextRequestFor() instead.'
           , WARNING)
        nav_tool=getToolByName(self, 'portal_navigation')
        return nav_tool.getNextRequestFor(context, action, status, **kwargs)

    security.declareProtected(CMFCorePermissions.ManagePortal, 'changeOwnershipOf')
    def changeOwnershipOf(self, object, owner, recursive=0):
        """ changes the ownership of an object """
        membership=getToolByName(self, 'portal_membership')
        if owner not in membership.listMemberIds():
            raise KeyError, 'Only users in this site can be made owners.'
        acl_users=getattr(self, 'acl_users')
        user = acl_users.getUser(owner)
        if user is not None:
            user= user.__of__(acl_users)
        else:
            from AccessControl import getSecurityManager
            user= getSecurityManager().getUser()

        object.changeOwnership(user, recursive) 
    
    security.declarePublic('urlparse')
    def urlparse(self, url):
        """ returns the pieces of url """
        return urlparse.urlparse(url)


    # Enable scripts to get the string value of an exception
    # even if the thrown exception is a string and not a
    # subclass of Exception.
    def exceptionString(self):
        s = sys.exc_info()[:2]  # don't assign the traceback to s (otherwise will generate a circular reference)
        if s[0] == None:
            return None
        if type(s[0]) == type(''):
            return s[0]
        return str(s[1])


    # provide a way of dumping an exception to the log even if we
    # catch it and otherwise ignore it
    def logException(self):
        """Dump an exception to the log"""
        log(summary=self.exceptionString(),
            text='\n'.join(traceback.format_exception(*sys.exc_info())),
            log_level=WARNING)
        

InitializeClass(PloneTool)

# These are monkey patched wrappers around CMF calls
# so that we can ensure we are really secure with
# emails

from Products.CMFDefault.RegistrationTool import RegistrationTool

oldMP = RegistrationTool.mailPassword
def mailPassword(self, forgotten_userid, REQUEST):
    """ Wrapper around mailPassword """
    membership = getToolByName(self, 'portal_membership')
    utils = getToolByName(self, 'plone_utils')
    member = membership.getMemberById(forgotten_userid)

    if member and member.getProperty('email'):
        # add the single email address
        if not utils.validateSingleEmailAddress(member.getProperty('email')):
            raise ValueError, 'The email address did not validate'

    return oldMP(self, forgotten_userid, REQUEST)

RegistrationTool.mailPassword = mailPassword

oldRN = RegistrationTool.registeredNotify

def registeredNotify(self, new_member_id):
    """ Wrapper around registeredNotify """
    membership = getToolByName( self, 'portal_membership' )
    utils = getToolByName(self, 'plone_utils')
    member = membership.getMemberById( new_member_id )
    
    if member and member.getProperty('email'):
        # add the single email address
        if not utils.validateSingleEmailAddress(member.getProperty('email')):
            raise ValueError, 'The email address did not validate'
    
    return oldRN(self, new_member_id)

RegistrationTool.registeredNotify = registeredNotify

