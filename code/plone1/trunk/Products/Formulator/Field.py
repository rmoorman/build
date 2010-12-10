from AccessControl import ClassSecurityInfo
from Acquisition.interfaces import IAcquirer
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from Persistence import Persistent
from Products.PageTemplates.Expressions import SecureModuleImporter
from Shared.DC.Scripts.Bindings import Bindings
import Acquisition
import OFS

import zope.cachedescriptors.property
from zope.i18nmessageid import MessageFactory

from Products.Formulator.Errors import ValidationError
from Products.Formulator.Widget import MultiItemsWidget
from Products.Formulator.helpers import (
    is_sequence, convert_unicode, key_to_id_re, id_value_re)


class Field:
    """Base class of all fields.
    A field is an object consisting of a widget and a validator.
    """
    security = ClassSecurityInfo()

    # this is a field
    is_field = 1
    # this is not an internal field (can be overridden by subclass)
    internal_field = 0
    # can alternatively render this field with Zope's :record syntax
    # this will be the record's name
    field_record = None

    def __init__(self, id, **kw):
        self.id = id
        # initialize values of fields in form
        self.initialize_values(kw)
        # initialize tales expression for fields in form
        self.initialize_tales()
        # initialize overrides of fields in form
        self.initialize_overrides()

        # initialize message values empty
        message_values = {}
        #for message_name in self.validator.message_names:
        #    message_values[message_name] = getattr(self.validator,
        #                                           message_name)
        self.message_values = message_values

    security.declareProtected('Change Formulator Fields', 'initialize_values')
    def initialize_values(self, dict):
        """Initialize values for properties, defined by fields in
        associated form.
        """
        values = {}
        for field in self.form.get_fields(include_disabled=1):
            id = field.id
            value = dict.get(id, field.get_value('default'))
            values[id] = value
        self.values = values

    security.declareProtected('Change Formulator Fields',
                              'initialize_tales')
    def initialize_tales(self):
        """Initialize tales expressions for properties (to nothing).
        """
        tales = {}
        for field in self.form.get_fields():
            id = field.id
            tales[id] = ""
        self.tales = tales

    security.declareProtected('Change Formulator Fields',
                              'initialize_overrides')
    def initialize_overrides(self):
        """Initialize overrides for properties (to nothing).
        """
        overrides = {}
        for field in self.form.get_fields():
            id = field.id
            overrides[id] = ""
        self.overrides = overrides

    security.declareProtected('Access contents information', 'has_value')
    def has_value(self, id):
        """Return true if the field defines such a value.
        """
        if self.values.has_key(id) or self.form.has_field(id):
            return 1
        else:
            return 0

    security.declareProtected('Access contents information', 'get_orig_value')
    def get_orig_value(self, id):
        """Get value for id; don't do any override calculation.
        """
        if self.values.has_key(id):
            return self.values[id]
        else:
            return self.form.get_field(id).get_value('default')

    security.declareProtected('Access contents information', 'get_value')
    def get_value(self, id, **kw):
        """Get value for id.

        Optionally pass keyword arguments that get passed to TALES
        expression.
        """
        tales_expr = self.tales.get(id, "")

        if tales_expr:
            # In old Zope version, for some reason, path expressions
            # expect 'here' and 'request' to exist, otherwise they
            # seem to fail. python expressions don't seem to have this
            # problem. However on newer version, it's fixed, and you
            # might not have request available as self.REQUEST (if
            # your field is in a Zope utility).

            # add 'here' if not in kw
            if not kw.has_key('here'):
                kw['here'] = self.aq_parent
            if hasattr(self, 'REQUEST'):
                kw['request'] = self.REQUEST
            kw['modules'] = SecureModuleImporter
            value = tales_expr.__of__(self)(
                field=self,
                form=self.aq_parent, **kw)
        else:
            override = self.overrides.get(id, "")
            if override:
                # call wrapped method to get answer
                value = override.__of__(self)()
            else:
                # get normal value
                value = self.get_orig_value(id)

        # if normal value can be wrapped in Acquisition, do it
        if IAcquirer.providedBy(value):
            return value.__of__(self)

        # create message id for title and description in right domain
        if id in ['title', 'description']:
            i18n_domain = self.get_i18n_domain()
            if i18n_domain:
                return MessageFactory(i18n_domain)(value)
        return value

    # this also works if field is not in form for testing
    # reasons..
    def get_i18n_domain(self):
        try:
            # try to acquire it
            return self.aq_inner.aq_parent.get_i18n_domain()
        except AttributeError:
            # otherwise, return empty domain
            return ''

    security.declareProtected('View management screens', 'get_override')
    def get_override(self, id):
        """Get override method for id (not wrapped)."""
        return self.overrides.get(id, "")

    security.declareProtected('View management screens', 'get_tales')
    def get_tales(self, id):
        """Get tales expression method for id."""
        return self.tales.get(id, "")

    security.declareProtected('Access contents information', 'is_required')
    def is_required(self):
        """Check whether this field is required (utility function)
        """
        return self.has_value('required') and self.get_value('required')

    security.declareProtected('View management screens', 'get_error_names')
    def get_error_names(self):
        """Get error messages.
        """
        return self.validator.message_names

    security.declareProtected('Access contents information',
                              'generate_field_key')
    def generate_field_key(self, validation=0):
        """Generate the key used to render the field in the form.
        """
        if self.field_record is None:
            return 'field_%s' % self.id
        elif validation:
            return self.id
        elif isinstance(self.widget, MultiItemsWidget):
            return "%s.%s:record:list" % (self.field_record, self.id)
        else:
            return '%s.%s:record' % (self.field_record, self.id)

    security.declareProtected('Access contents information',
                              'generate_field_key')
    def generate_field_html_id(self, key=None, validation=0):
        """Generate the html id used to render the field in the form.
           The id is generated as follows:
             the `key` param is prefixed with the name of the form the field is
             in and then sanitized to be an xml id addressable by css (i.e.
             [._ :] converted to '-'

           Note that if a field's "extra" parameter has an ID attribute
           in it, the value of the ID attribute is used rather than the
           generated one described above.  This is for backward compatibility.

           The `key` param is useful for subfields (e.g. DateTime).  The
           DateTimeWidget's render function needs to compute the subfield_key,
           and pass it into this function, since the subfield does not know
           what field it is a part of.

           Widgets can add this as the 'ID' attribute of rendered elements.
           The presentation layer can use this id in <label> tags, however using
           the 'html_id' property is preferred."""

        #if the 'extra' parameter has an ID attribute in it, use the value
        # of the ID
        if self.has_value('extra'):
            res = id_value_re.search(self.get_value('extra'))
            if res:
                return res.group(1)

        #generate the key if one wasn't passed in
        if not key:
            key = self.generate_field_key(validation)

        #if the field is acquisition wrapped, has a Form as a parent
        # and the form's `name` attribute != the default of 'form',
        # prefix it to the id, to add 'uniqueness'.
        #NOTE: subfields of datetime are not acquisition wrapped,
        #      so this does not work for them.
        name = None
        if hasattr(self,'aq_parent'):
            #name is an attribute of Formulator.Form, but not all
            # formulator fields have Forms as parents.  An example
            # is a SilvaMetadata element.  Fields of metadata elements
            # have a field_record = metadata name, which is part of the
            # key
            parent = self.aq_parent
            #in case a form is not acquisition wrapped
            #  (e.g. like in the tests)
            if hasattr(parent, 'aq_explicit'):
                name = getattr(parent.aq_explicit,'name',None)
            else:
                name = getattr(parent, 'name', None)
        if name is not None and name != 'form':
            key = '%s%s'%(name,key)
        return key_to_id_re.sub('-',key)

    @zope.cachedescriptors.property.CachedProperty
    def html_id(self):
        """html_id returns the html id for the field.
           presentation code can call this property to retrieve
           the html id for the field.

           See generate_field_html_id, which actually does
           the work."""
        return self.generate_field_html_id()

    def generate_subfield_key(self, id, validation=0):
        """Generate the key used to render a sub field.
        """
        if self.field_record is None or validation:
            return 'subfield_%s_%s'%(self.id, id)
        return '%s.subfield_%s_%s:record' % (self.field_record, self.id, id)

    security.declareProtected('View management screens', 'get_error_message')
    def get_error_message(self, name, want_message_id=True):
        try:
            # look up message in field
            result = self.message_values[name]
        except KeyError:
            # if we can't find it in field, look it up in form
            # these will be the correct message ids, so return result
            # directly
            if name in self.validator.message_names:
                result = getattr(self.validator, name)
            else:
                result = "Unknown error: %s" % name
            # if we don't want message id, strip it off
            if not want_message_id:
                try:
                    # convert message id into unicode string
                    result = unicode(result)
                except AttributeError:
                    pass
            return result
        else:
            if want_message_id:
                # we do want a message id, so construct one from form domain
                result = MessageFactory(self.get_i18n_domain())(result)
            return result

    security.declarePrivate('_render_helper')
    def _render_helper(self, key, value, REQUEST):
        value = self._get_default(key, value, REQUEST)
        if self.get_value('hidden'):
            return self.widget.render_hidden(self, key, value, REQUEST)
        else:
            return self.widget.render(self, key, value, REQUEST)

    security.declarePrivate('_get_default')
    def _get_default(self, key, value, REQUEST):
        if value is not None:
            return value
        try:
            value = REQUEST.form[key]
        except (KeyError, AttributeError):
            # fall back on default
            return self.get_value('default')

        # if we enter a string value while the field expects unicode,
        # convert to unicode first
        # this solves a problem when re-rendering a sticky form with
        # values from request
        if (self.has_value('unicode') and self.get_value('unicode')):
            value = convert_unicode(value, self.get_form_encoding())

        return value

    security.declareProtected('View', 'render')
    def render(self, value=None, REQUEST=None):
        """Render the field widget.
        value -- the value the field should have (for instance
                 from validation).
        REQUEST -- REQUEST can contain raw (unvalidated) field
                 information. If value is None, REQUEST is searched
                 for this value.
        if value and REQUEST are both None, the 'default' property of
        the field will be used for the value.
        """
        return self._render_helper(self.generate_field_key(), value, REQUEST)

    security.declareProtected('View', 'render_view')
    def render_view(self, value):
        """Render value to be viewed.
        """
        return self.widget.render_view(self, value)

    security.declareProtected('View', 'render_from_request')
    def render_from_request(self, REQUEST):
        """Convenience method; render the field widget from REQUEST
        (unvalidated data), or default if no raw data is found.
        """
        return self._render_helper(self.generate_field_key(), None, REQUEST)

    security.declareProtected('View', 'render_sub_field')
    def render_sub_field(self, id, value=None, REQUEST=None):
        """Render a sub field, as part of complete rendering of widget in
        a form. Works like render() but for sub field.
        """
        return self.sub_form.get_field(id)._render_helper(
            self.generate_subfield_key(id), value, REQUEST)

    security.declareProtected('View', 'render_sub_field_from_request')
    def render_sub_field_from_request(self, id, REQUEST):
        """Convenience method; render the field widget from REQUEST
        (unvalidated data), or default if no raw data is found.
        """
        return self.sub_form.get_field(id)._render_helper(
            self.generate_subfield_key(id), None, REQUEST)

    security.declarePrivate('_validate_helper')
    def _validate_helper(self, key, REQUEST):
        value = self.validator.validate(self, key, REQUEST)
        # now call external validator after all other validation
        external_validator = self.get_value('external_validator')
        if external_validator and not external_validator(value, REQUEST):
            self.validator.raise_error('external_validator_failed', self)
        return value

    security.declareProtected('View', 'validate')
    def validate(self, REQUEST):
        """Validate/transform the field.
        """
        return self._validate_helper(
            self.generate_field_key(validation=1), REQUEST)

    security.declareProtected('View', 'need_validate')
    def need_validate(self, REQUEST):
        """Return true if validation is needed for this field.
        """
        return self.validator.need_validate(
            self, self.generate_field_key(validation=1), REQUEST)

    security.declareProtected('View', 'validate_sub_field')
    def validate_sub_field(self, id, REQUEST):
        """Validates a subfield (as part of field validation).
        """
        return self.sub_form.get_field(id)._validate_helper(
            self.generate_subfield_key(id, validation=1), REQUEST)

InitializeClass(Field)


class ZMIField(
    Acquisition.Implicit,
    Persistent,
    OFS.SimpleItem.Item,
    Field,
    ):
    """Base class for a field implemented as a Python (file) product.
    """
    security = ClassSecurityInfo()

    security.declareObjectProtected('View')

    # the various tabs of a field
    manage_options = (
        {'label':'Edit',       'action':'manage_main',
         'help':('Formulator', 'fieldEdit.txt')},
        {'label':'TALES',      'action':'manage_talesForm',
         'help':('Formulator', 'fieldTales.txt')},
        {'label':'Override',    'action':'manage_overrideForm',
         'help':('Formulator', 'fieldOverride.txt')},
        {'label':'Messages',   'action':'manage_messagesForm',
         'help':('Formulator', 'fieldMessages.txt')},
        {'label':'Test',       'action':'fieldTest',
         'help':('Formulator', 'fieldTest.txt')},
        ) + OFS.SimpleItem.SimpleItem.manage_options

    security.declareProtected('View', 'title')
    def title(self):
        """The title of this field."""
        return self.get_value('title')

    # display edit screen as main management screen
    security.declareProtected('View management screens', 'manage_main')
    manage_main = DTMLFile('dtml/fieldEdit', globals())

    security.declareProtected('Change Formulator Fields', 'manage_edit')
    def manage_edit(self, REQUEST):
        """Submit Field edit form.
        """
        try:
            # validate the form and get results
            result = self.form.validate(REQUEST)
        except ValidationError, err:
            if REQUEST:
                message = "Error: %s - %s" % (err.field.get_value('title'),
                                              err.error_text)
                return self.manage_main(self,REQUEST,
                                        manage_tabs_message=message)
            else:
                raise

        self._edit(result)

        if REQUEST:
            message="Content changed."
            return self.manage_main(self,REQUEST,
                                    manage_tabs_message=message)

    security.declareProtected('Change Formulator Fields', 'manage_edit_xmlrpc')
    def manage_edit_xmlrpc(self, map):
        """Edit Field Properties through XMLRPC
        """
        # BEWARE: there is no validation on the values passed through the map
        self._edit(map)

    def _edit(self, result):
        # first check for any changes
        values = self.values
        # if we are in unicode mode, convert result to unicode
        # acquire get_unicode_mode from form..
        if self.get_unicode_mode():
            result = convert_unicode(result, self.get_form_encoding())

        changed = []
        for key, value in result.items():
            # store keys for which we want to notify change
            if not values.has_key(key) or values[key] != value:
                changed.append(key)

        # now do actual update of values
        values.update(result)
        self.values = values

        # finally notify field of all changed values if necessary
        for key in changed:
            method_name = "on_value_%s_changed" % key
            if hasattr(self, method_name):
                getattr(self, method_name)(values[key])


##     security.declareProtected('Change Formulator Forms', 'manage_beforeDelete')
##     def manage_beforeDelete(self, item, container):
##         """Remove name from list if object is deleted.
##         """
##         # update group info in form
##         if hasattr(item.aq_explicit, 'is_field'):
##             container.field_removed(item.id)

##     security.declareProtected('Change Formulator Forms', 'manage_afterAdd')
##     def manage_afterAdd(self, item, container):
##         """What happens when we add a field.
##         """
##         # update group info in form
##         if hasattr(item.aq_explicit, 'is_field'):
##             container.field_added(item.id)

    # methods screen
    security.declareProtected('View management screens',
                              'manage_overrideForm')
    manage_overrideForm = DTMLFile('dtml/fieldOverride', globals())

    security.declareProtected('Change Formulator Forms', 'manage_override')
    def manage_override(self, REQUEST):
        """Change override methods.
        """
        try:
            # validate the form and get results
            result = self.override_form.validate(REQUEST)
        except ValidationError, err:
            if REQUEST:
                message = "Error: %s - %s" % (err.field.get_value('title'),
                                              err.error_text)
                return self.manage_overrideForm(self,REQUEST,
                                                manage_tabs_message=message)
            else:
                raise

        # update overrides of field with results
        if not hasattr(self, "overrides"):
            self.overrides = result
        else:
            self.overrides.update(result)
            self.overrides = self.overrides

        if REQUEST:
            message="Content changed."
            return self.manage_overrideForm(self,REQUEST,
                                            manage_tabs_message=message)

    # tales screen
    security.declareProtected('View management screens',
                              'manage_talesForm')
    manage_talesForm = DTMLFile('dtml/fieldTales', globals())

    security.declareProtected('Change Formulator Forms', 'manage_tales')
    def manage_tales(self, REQUEST):
        """Change TALES expressions.
        """
        try:
            # validate the form and get results
            result = self.tales_form.validate(REQUEST)
        except ValidationError, err:
            if REQUEST:
                message = "Error: %s - %s" % (err.field.get_value('title'),
                                              err.error_text)
                return self.manage_talesForm(self,REQUEST,
                                             manage_tabs_message=message)
            else:
                raise

        self._edit_tales(result)

        if REQUEST:
            message="Content changed."
            return self.manage_talesForm(self, REQUEST,
                                         manage_tabs_message=message)

    def _edit_tales(self, result):
        if not hasattr(self, 'tales'):
            self.tales = result
        else:
            self.tales.update(result)
            self.tales = self.tales

    security.declareProtected('Change Formulator Forms', 'manage_tales_xmlrpc')
    def manage_tales_xmlrpc(self, map):
        """Change TALES expressions through XMLRPC.
        """
        # BEWARE: there is no validation on the values passed through the map
        from TALESField import TALESMethod
        result = {}
        for key, value in map.items():
            result[key] = TALESMethod(value)
        self._edit_tales(result)

    # display test screen
    security.declareProtected('View management screens', 'fieldTest')
    fieldTest = DTMLFile('dtml/fieldTest', globals())

    # messages screen
    security.declareProtected('View management screens', 'manage_messagesForm')
    manage_messagesForm = DTMLFile('dtml/fieldMessages', globals())

    # field list header
    security.declareProtected('View management screens', 'fieldListHeader')
    fieldListHeader = DTMLFile('dtml/fieldListHeader', globals())

    # field description display
    security.declareProtected('View management screens', 'fieldDescription')
    fieldDescription = DTMLFile('dtml/fieldDescription', globals())

    security.declareProtected('Change Formulator Fields', 'manage_messages')
    def manage_messages(self, REQUEST):
        """Change message texts.
        """
        messages = self.message_values
        unicode_mode = self.get_unicode_mode()
        for message_key in self.get_error_names():
            message = REQUEST[message_key]
            if unicode_mode:
                message = unicode(message, 'UTF-8')
            # only save message if we're indeed changing from original
            if getattr(self.validator, message_key) != message:
                messages[message_key] = message

        self.message_values = messages
        if REQUEST:
            message="Content changed."
            return self.manage_messagesForm(self,REQUEST,
                                            manage_tabs_message=message)

    security.declareProtected('View', 'index_html')
    def index_html(self, REQUEST):
        """Render this field.
        """
        return self.render(REQUEST=REQUEST)

    security.declareProtected('Access contents information', '__getitem__')
    def __getitem__(self, key):
        return self.get_value(key)

    security.declareProtected('View management screens', 'isTALESAvailable')
    def isTALESAvailable(self):
        """Return true only if TALES is available.
        """
        try:
            from Products.PageTemplates.Expressions import getEngine
            return 1
        except ImportError:
            return 0

InitializeClass(ZMIField)
PythonField = ZMIField # NOTE: for backwards compatibility

class ZClassField(Field):
    """Base class for a field implemented as a ZClass.
    """
    pass


def field_added(the_object, event):
    # update group info in form
    if the_object != event.object:
        return
    event.newParent.field_added(the_object.id)

def field_removed(the_object, event):
     # update group info in form
    if the_object != event.object:
        return
    event.oldParent.field_removed(the_object.id)
