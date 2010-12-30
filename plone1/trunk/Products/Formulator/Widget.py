import string, types
from DummyField import fields
from DocumentTemplate.DT_Util import html_quote
from DateTime import DateTime
from helpers import is_sequence, id_value_re


class Widget:
    """A field widget that knows how to display itself as HTML.
    """

    property_names = ['title', 'description',
                      'default', 'css_class', 'alternate_name',
                      'hidden']

    title = fields.StringField('title',
                               title='Title',
                               description=(
        "The title of this field. This is the title of the field that "
        "will appear in the form when it is displayed. Required."),
                               default="",
                               required=1)

    description = fields.TextAreaField('description',
                                       title='Description',
                                       description=(
        "Description of this field. The description property can be "
        "used to add a short description of what a field does; such as "
        "this one."),
                                       default="",
                                       width="20", height="3",
                                       required=0)

    css_class = fields.StringField('css_class',
                                   title='CSS class',
                                   description=(
        "The CSS class of the field. This can be used to style your "
        "formulator fields using cascading style sheets. Not required."),
                                   default="",
                                   required=0)

    alternate_name = fields.StringField('alternate_name',
                                        title='Alternate name',
                                        description=(
        "An alternative name for this field. This name will show up in "
        "the result dictionary when doing validation, and in the REQUEST "
        "if validation goes to request. This can be used to support names "
        "that cannot be used as Zope ids."),
                                        default="",
                                        required=0)

    hidden = fields.CheckBoxField('hidden',
                                  title="Hidden",
                                  description=(
        "This field will be on the form, but as a hidden field. The "
        "contents of the hidden field will be the default value. "
        "Hidden fields are not visible but will be validated."),
                                  default=0)

    # NOTE: for ordering reasons (we want extra at the end),
    # this isn't in the base class property_names list, but
    # instead will be referred to by the subclasses.
    extra = fields.StringField('extra',
                               title='Extra',
                               description=(
        "A string containing extra HTML code for attributes. This "
        "string will be literally included in the rendered field."
        "This property can be useful if you want "
        "to add an onClick attribute to use with JavaScript, for instance."),
                               default="",
                               required=0)
 
    #this property is used to determine whether the widget
    # uses an html id (e.g. the widget has a single or primary
    # input), so that the presentation can wrap the field
    # title within a label or not.
    has_html_id = True

    def render(self, field, key, value, REQUEST):
        """Renders this widget as HTML using property values in field.
        """
        return "[widget]"

    def render_hidden(self, field, key, value, REQUEST):
        """Renders this widget as a hidden field.
        """
        try:
            extra = field.get_value('extra')
        except KeyError:
            # In case extra is not defined as in DateTimeWidget
            extra = ''
        kw = {'type': "hidden",
              'name': key,
              'value': value,
              'extra': extra }
        if not extra or not id_value_re.search(extra):
            kw['id'] = field.generate_field_html_id(key)
        return render_element("input", **kw)

    def render_view(self, field, value):
        """Renders this widget for public viewing.
        """
        # default implementation
        if value is None:
            return ''
        return value


class TextWidget(Widget):
    """Text widget
    """
    property_names = Widget.property_names +\
                     ['display_width', 'display_maxwidth', 'extra']

    default = fields.StringField('default',
                                 title='Default',
                                 description=(
        "You can place text here that will be used as the default "
        "value of the field, unless the programmer supplies an override "
        "when the form is being generated."),
                                 default="",
                                 required=0)

    display_width = fields.IntegerField('display_width',
                                        title='Display width',
                                        description=(
        "The width in characters. Required."),
                                        default=20,
                                        required=1)

    display_maxwidth = fields.IntegerField('display_maxwidth',
                                           title='Maximum input',
                                           description=(
        "The maximum input in characters that the widget will allow. "
        "Required. If set to 0 or is left empty, there is no maximum. "
        "Note that is client side behavior only."),
                                           default="",
                                           required=0)

    def render(self, field, key, value, REQUEST):
        """Render text input field.
        """
        extra = field.get_value('extra')
        kw = {'type': "text",
                'name' : key,
                'css_class' : field.get_value('css_class'),
                'value' : value,
                'size' : field.get_value('display_width'),
                'extra': extra}
        if not extra or not id_value_re.search(extra):
            kw['id'] = field.generate_field_html_id(key)
        display_maxwidth = field.get_value('display_maxwidth') or 0
        if display_maxwidth > 0:
            kw['maxlength'] = display_maxwidth
        return render_element("input", **kw)

    def render_view(self, field, value):
        if value is None:
            return ''
        return value

TextWidgetInstance = TextWidget()

class PasswordWidget(TextWidget):

    def render(self, field, key, value, REQUEST):
        """Render password input field.
        """
        extra = field.get_value('extra')
        kw = {'type': "password",
              'name': key,
              'css_class': field.get_value('css_class'),
              'value': value,
              'size': field.get_value('display_width'),
              'extra': extra}
    
        if not extra or not id_vlaue_re.search(extra):
            kw['id'] = field.generate_field_html_id(key)

        display_maxwidth = field.get_value('display_maxwidth') or 0
        if display_maxwidth > 0:
            kw['maxlength'] = display_maxwidth
        return render_element("input", **kw)

    def render_view(self, field, value):
        return "[password]"

PasswordWidgetInstance = PasswordWidget()

class CheckBoxWidget(Widget):
    property_names = Widget.property_names + ['extra']

    default = fields.CheckBoxField('default',
                                   title='Default',
                                   description=(
        "Default setting of the widget; either checked or unchecked. "
        "(true or false)"),
                                   default=0)

    def render(self, field, key, value, REQUEST):
        """Render checkbox.
        """
        extra = field.get_value('extra')
        kw = {'type': "checkbox",
              'name': key,
              'css_class': field.get_value('css_class'),
              'extra': extra
              }
        if not extra or not id_value_re.search(extra):
            kw['id'] = field.generate_field_html_id(key)
        if value:
            kw['checked']=None
        contents = render_element("input", **kw)
        return render_element('label', contents=contents)

    def render_view(self, field, value):
        if value:
            return 1
        else:
            return 0

CheckBoxWidgetInstance = CheckBoxWidget()

class TextAreaWidget(Widget):
    """Textarea widget
    """
    property_names = Widget.property_names +\
                     ['width', 'height', 'extra']

    default = fields.TextAreaField('default',
                                   title='Default',
                                   description=(
        "Default value of the text in the widget."),
                                   default="",
                                   width=20, height=3,
                                   required=0)

    width = fields.IntegerField('width',
                                title='Width',
                                description=(
        "The width (columns) in characters. Required."),
                                default=40,
                                required=1)

    height = fields.IntegerField('height',
                                 title="Height",
                                 description=(
        "The height (rows) in characters. Required."),
                                 default=5,
                                 required=1)

    def render(self, field, key, value, REQUEST):
        width = field.get_value('width')
        height = field.get_value('height')
        extra=field.get_value('extra')
        kw = {'name': key,
              'css_class': field.get_value('css_class'),
              'cols': width,
              'rows': height,
              'contents': html_quote(value)}
        if not extra or not id_value_re.search(extra):
            kw['id'] = field.generate_field_html_id(key)
        return render_element("textarea", **kw)

    def render_view(self, field, value):
        if value is None:
            return ''
        return value

TextAreaWidgetInstance = TextAreaWidget()

class LinesTextAreaWidget(TextAreaWidget):
    property_names = Widget.property_names +\
                     ['width', 'height', 'view_separator', 'extra']

    default = fields.LinesField('default',
                                title='Default',
                                description=(
        "Default value of the lines in the widget."),
                                default=[],
                                width=20, height=3,
                                required=0)

    view_separator = fields.StringField('view_separator',
                                        title='View separator',
                                        description=(
        "When called with render_view, this separator will be used to "
        "render individual items."),
                                        width=20,
                                        default='<br />\n',
                                        whitespace_preserve=1,
                                        required=1)

    def render(self, field, key, value, REQUEST):
        if is_sequence(value):
            value = string.join(value, "\n")
        return TextAreaWidget.render(self, field, key, value, REQUEST)

    def render_view(self, field, value):
        if value is None:
            return ''
        return string.join(value, field.get_value('view_separator'))

    def render_hidden(self, field, key, value, REQUEST):
        if value is None:
            return ''
        if is_sequence(value):
            value = '\n'.join(value)
        # reuse method from base class
        return Widget.render_hidden(self,field,key, value, REQUEST)


LinesTextAreaWidgetInstance = LinesTextAreaWidget()

class FileWidget(TextWidget):

    def render(self, field, key, value, REQUEST):
        """Render text input field.
        """
        extra=field.get_value('extra')
        kw = {'type': "file",
              'name': key,
              'css_class': field.get_value('css_class'),
              'value': value,
              'size': field.get_value('display_width'),
              'extra': extra}

        if not extra or not id_value_re.search(extra):
            kw['id'] = field.generate_field_html_id(key)

        display_maxwidth = field.get_value('display_maxwidth') or 0
        if display_maxwidth > 0:
            kw['maxlength'] = display_maxwidth
        return render_element("input", **kw)

    def render_view(self, field, value):
        return "[File]"

FileWidgetInstance = FileWidget()

class ItemsWidget(Widget):
    """A widget that has a number of items in it.
    """

    items = fields.ListTextAreaField('items',
                                     title='Items',
                                     description=(
        "Items in the field. Each row should contain an "
        "item. Use the | (pipe) character to separate what is shown "
        "to the user from the submitted value. If no | is supplied, the "
        "shown value for the item will be identical to the submitted value. "
        "Internally the items property returns a list. If a list item "
        "is a single value, that will be used for both the display and "
        "the submitted value. A list item can also be a tuple consisting "
        "of two elements. The first element of the tuple should be a string "
        "that is name of the item that should be displayed. The second "
        "element of the tuple should be the value that will be submitted. "
        "If you want to override this property you will therefore have "
        "to return such a list."),

                                     default=[],
                                     width=20,
                                     height=5,
                                     required=0)

    # NOTE: for ordering reasons (we want extra at the end),
    # this isn't in the base class property_names list, but
    # instead will be referred to by the subclasses.
    extra_item = fields.StringField('extra_item',
                               title='Extra per item',
                               description=(
        "A string containing extra HTML code for attributes. This "
        "string will be literally included each of the rendered items of the "
        "field. This property can be useful if you want "
        "to add a disabled attribute to disable all contained items, for "
        "instance."),
                               default="",
                               required=0)

class SingleItemsWidget(ItemsWidget):
    """A widget with a number of items that has only a single
    selectable item.
    """
    default = fields.StringField('default',
                                 title='Default',
                                 description=(
        "The default value of the widget; this should be one of the "
        "elements in the list of items."),
                                 default="",
                                 required=0)

    first_item = fields.CheckBoxField('first_item',
                                      title="Select First Item",
                                      description=(
        "If checked, the first item will always be selected if "
        "no initial default value is supplied."),
                                      default=0)

    def render_items(self, field, key, value, REQUEST):

        # get items
        items = field.get_value('items')

        # check if we want to select first item
        if not value and field.get_value('first_item') and len(items) > 0:
            if is_sequence(items[0]):
                text, value = items[0]
            else:
                value = items[0]

        css_class = field.get_value('css_class')
        extra_item = field.get_value('extra_item')

        field_html_id = None
        if not extra_item or not id_value_re.search(extra_item):
            field_html_id = field.generate_field_html_id(key)
        
        # if we run into multiple items with same value, we select the
        # first one only (for now, may be able to fix this better later)
        selected_found = 0
        rendered_items = []
        index = 0
        for item in items:
            index += 1
            if is_sequence(item):
                item_text, item_value = item
            else:
                item_text = item
                item_value = item

            item_id = field_html_id and field_html_id + str(index) or None
            if item_value == value and not selected_found:
                rendered_item = self.render_selected_item(item_text,
                                                          item_value,
                                                          key,
                                                          css_class,
                                                          extra_item,
                                                          item_id)
                selected_found = 1
            else:
                rendered_item = self.render_item(item_text,
                                                 item_value,
                                                 key,
                                                 css_class,
                                                 extra_item,
                                                 item_id)

            rendered_items.append(rendered_item)

        return rendered_items

    def render_view(self, field, value):
        if value is None or value == '':
            # check for empty string too, for situations
            # where no default value is set.
            return ''
        items = field.get_value('items')
        for item in items:
            if is_sequence(item):
                item_text, item_value = item
            else:
                item_text = item
                item_value = item
            if value == item_value:
                return item_text
        raise KeyError, "Wrong item value [[%s]]" % (value,)

class MultiItemsWidget(ItemsWidget):
    """A widget with a number of items that has multiple selectable
    items.
    """
    default = fields.LinesField('default',
                                title='Default',
                                description=(
        "The initial selections of the widget. This is a list of "
        "zero or more values. If you override this property from Python "
        "your code should return a Python list."),
                                width=20, height=3,
                                default=[],
                                required=0)

    view_separator = fields.StringField('view_separator',
                                        title='View separator',
                                        description=(
        "When called with render_view, this separator will be used to "
        "render individual items."),
                                        width=20,
                                        default='<br />\n',
                                        whitespace_preserve=1,
                                        required=1)

    def render_items(self, field, key, value, REQUEST):
        # need to deal with single item selects
        if not is_sequence(value):
            value = [value]

        items = field.get_value('items')
        css_class = field.get_value('css_class')
        extra_item = field.get_value('extra_item')
        field_html_id = field.generate_field_html_id(key)
        index = 0
        rendered_items = []
        for item in items:
            index += 1
            if is_sequence(item):
                item_text, item_value = item
            else:
                item_text = item
                item_value = item

            if item_value in value:
                rendered_item = self.render_selected_item(item_text,
                                                          item_value,
                                                          key,
                                                          css_class,
                                                          extra_item,
                                                          field_html_id+str(index))
            else:
                rendered_item = self.render_item(item_text,
                                                 item_value,
                                                 key,
                                                 css_class,
                                                 extra_item,
                                                 field_html_id+str(index))

            rendered_items.append(rendered_item)

        return rendered_items

    def render_items_view(self, field, value):
        if not is_sequence(value):
            value = [value]

        items = field.get_value('items')
        d = {}
        for item in items:
            if is_sequence(item):
                item_text, item_value = item
            else:
                item_text = item
                item_value = item
            d[item_value] = item_text
        result = []
        for e in value:
            result.append(d[e])
        return result

    def render_view(self, field, value):
        if value is None:
            return ''
        return string.join(self.render_items_view(field, value),
                           field.get_value('view_separator'))

    def render_hidden(self, field, key, value, REQUEST):
        if value is not None and not is_sequence(value):
            value = [value]
        # reuse method from base class
        render_item_hidden = Widget.render_hidden
        result = []
        for v in value:
            result.append(render_item_hidden(self, field, key, v, REQUEST))
        return ''.join(result)

class ListWidget(SingleItemsWidget):
    """List widget.
    """
    property_names = Widget.property_names +\
                     ['first_item', 'items', 'size', 'extra', 'extra_item']

    size = fields.IntegerField('size',
                               title='Size',
                               description=(
        "The display size in rows of the field. If set to 1, the "
        "widget will be displayed as a drop down box by many browsers, "
        "if set to something higher, a list will be shown. Required."),
                               default=5,
                               required=1)

    def render(self, field, key, value, REQUEST):
        rendered_items = self.render_items(field, key, value, REQUEST)

        extra=field.get_value('extra')  
        kw = {'name': key,
              'css_class': field.get_value('css_class'),
              'size': field.get_value('size'),
              'contents': string.join(rendered_items, "\n"),
              'extra': extra}
        if not extra or not id_value_re.search(extra):
            kw['id'] = field.generate_field_html_id(key)
        return render_element('select', **kw)

    def render_item(self, text, value, key, css_class, extra_item, html_id):
        return render_element('option', contents=text, value=value,
                              extra=extra_item)

    def render_selected_item(self, text, value, key, css_class, extra_item, html_id):
        return render_element('option', contents=text, value=value,
                              selected=None, extra=extra_item)

ListWidgetInstance = ListWidget()

class MultiListWidget(MultiItemsWidget):
    """List widget with multiple select.
    """
    property_names = Widget.property_names +\
                     ['items', 'size', 'view_separator', 'extra', 'extra_item']

    size = fields.IntegerField('size',
                               title='Size',
                               description=(
        "The display size in rows of the field. If set to 1, the "
        "widget will be displayed as a drop down box by many browsers, "
        "if set to something higher, a list will be shown. Required."),
                               default=5,
                               required=1)

    def render(self, field, key, value, REQUEST):
        rendered_items = self.render_items(field, key, value, REQUEST)

        extra = field.get_value('extra')
        kw = {'name': key,
              'multiple': None,
              'css_class': field.get_value('css_class'),
              'size': field.get_value('size'),
              'contents': string.join(rendered_items, "\n"),
              'extra': extra }
        if not extra or not id_value_re.search(extra):
            kw['id'] = field.generate_field_html_id(key)
        return render_element('select', **kw)

    def render_item(self, text, value, key, css_class, extra_item, html_id):
        return render_element('option', contents=text, value=value,
                              extra=extra_item)

    def render_selected_item(self, text, value, key, css_class, extra_item, html_id):
        return render_element('option', contents=text, value=value,
                              selected=None, extra=extra_item)

MultiListWidgetInstance = MultiListWidget()

class RadioWidget(SingleItemsWidget):
    """radio buttons widget.
    """
    property_names = Widget.property_names +\
                     ['first_item', 'items', 'orientation', 'extra_item']

    orientation = fields.ListField('orientation',
                                   title='Orientation',
                                   description=(
        "Orientation of the radio buttons. The radio buttons will "
        "be drawn either vertically or horizontally."),
                                   default="vertical",
                                   required=1,
                                   size=1,
                                   items=[('Vertical', 'vertical'),
                                          ('Horizontal', 'horizontal')])
    
    has_html_id = False

    def render(self, field, key, value, REQUEST):
        rendered_items = self.render_items(field, key, value, REQUEST)
        orientation = field.get_value('orientation')
        if orientation == 'horizontal':
            return string.join(rendered_items, "&nbsp;&nbsp;")
        else:
            return string.join(rendered_items, "<br />")

    def render_item(self, text, value, key, css_class, extra_item, html_id):
        kw = {'type': "radio",
              'css_class': css_class,
              'name': key,
              'value': value,
              'extra': extra_item}
        if html_id:
            kw['id'] = html_id
        contents = render_element('input', **kw) + text
        return render_element('label', contents=contents)

    def render_selected_item(self, text, value, key, css_class, extra_item, html_id):
        kw = {'type': "radio",
              'css_class': css_class,
              'name': key,
              'value': value,
              'checked': None,
              'extra': extra_item}
        if html_id:
            kw['id'] = html_id
        contents = render_element('input', **kw) + text
        return render_element('label', contents=contents)

RadioWidgetInstance = RadioWidget()

class MultiCheckBoxWidget(MultiItemsWidget):
    """multiple checkbox widget.
    """
    property_names = Widget.property_names +\
                     ['items', 'orientation', 'view_separator', 'extra_item']

    orientation = fields.ListField('orientation',
                                   title='Orientation',
                                   description=(
        "Orientation of the check boxes. The check boxes will "
        "be drawn either vertically or horizontally."),
                                   default="vertical",
                                   required=1,
                                   size=1,
                                   items=[('Vertical', 'vertical'),
                                          ('Horizontal', 'horizontal')])

    has_html_id = False

    def render(self, field, key, value, REQUEST):
        rendered_items = self.render_items(field, key, value, REQUEST)
        orientation = field.get_value('orientation')
        if orientation == 'horizontal':
            return string.join(rendered_items, "&nbsp;&nbsp;")
        else:
            return string.join(rendered_items, "<br />")

    def render_item(self, text, value, key, css_class, extra_item, html_id):
        kw = {'type': "checkbox",
              'css_class': css_class,
              'name': key,
              'value': value,
              'extra': extra_item}
        if html_id:
            kw['id'] = html_id
        contents = render_element('input', **kw) + text
        return render_element('label', contents=contents)

    def render_selected_item(self, text, value, key, css_class, extra_item, html_id):
        kw = {'type': "checkbox",
              'css_class': css_class,
              'name': key,
              'value': value,
              'checked': None,
              'extra': extra_item}
        if html_id:
            kw['id'] = html_id
        contents = render_element('input', **kw) + text
        return render_element('label', contents=contents)

MultiCheckBoxWidgetInstance = MultiCheckBoxWidget()

class DateTimeWidget(Widget):
    property_names = Widget.property_names +\
                     ['default_now', 'date_separator', 'time_separator',
                      'input_style', 'input_order',
                      'date_only', 'hide_day', 'ampm_time_style', 'calendar_picker', 'calendar_start']

    default = fields.DateTimeField('default',
                                   title="Default",
                                   description=("The default datetime."),
                                   default=None,
                                   display_style="text",
                                   display_order="ymd",
                                   input_style="text",
                                   required=0)

    default_now = fields.CheckBoxField('default_now',
                                       title="Default to now",
                                       description=(
        "Default date and time will be the date and time at showing of "
        "the form (if the default is left empty)."),
                                       default=0)

    date_separator = fields.StringField('date_separator',
                                        title='Date separator',
                                        description=(
        "Separator to appear between year, month, day."),
                                        default="/",
                                        required=0,
                                        display_width=2,
                                        display_maxwith=2,
                                        max_length=2)

    time_separator = fields.StringField('time_separator',
                                        title='Time separator',
                                        description=(
        "Separator to appear between hour and minutes."),
                                        default=":",
                                        required=0,
                                        display_width=2,
                                        display_maxwith=2,
                                        max_length=2)

    input_style = fields.ListField('input_style',
                                   title="Input style",
                                   description=(
        "The type of input used. 'text' will show the date part "
        "as text, while 'list' will use dropdown lists instead."),
                                   default="text",
                                   items=[("text", "text"),
                                          ("list", "list")],
                                   size=1)

    input_order = fields.ListField('input_order',
                                   title="Input order",
                                   description=(
        "The order in which date input should take place. Either "
        "year/month/day, day/month/year or month/day/year."),
                                   default="ymd",
                                   items=[("year/month/day", "ymd"),
                                          ("day/month/year", "dmy"),
                                          ("month/day/year", "mdy")],
                                   required=1,
                                   size=1)

    date_only = fields.CheckBoxField('date_only',
                                     title="Display date only",
                                     description=(
        "Display the date only, not the time."),
                                     default=0)

    hide_day = fields.CheckBoxField('hide_day',
                                           title="Hide day field",
                                           description=(
        "Hide the day field."),
                                           default=0)

    ampm_time_style = fields.CheckBoxField('ampm_time_style',
                                           title="AM/PM time style",
                                           description=(
        "Display time in am/pm format."),
                                           default=0)
    calendar_picker = fields.CheckBoxField('calendar_picker',
                                           title="Enable calendar picker",
                                           description=(
        "Displays a floating calendar to select the date.  "
        "The js calendar is located here: http://www.dynarch.com/projects/calendar/old/"),
                                           default=0)

    calendar_start = fields.ListField('calendar_start',
                                      title="Starting day of week",
                                      description=(
        "The starting day of the week for the floating calendar."),
                                      default="Sunday",
                                      items=[("Sunday", "0"),
                                             ("Monday", "1"),
                                             ("Tuesday", "2"),
                                             ("Wednesday", "3"),
                                             ("Thursday", "4"),
                                             ("Friday", "5"),
                                             ("Saturday", "6"),],
                                      required=0,
                                      size=1)

    has_html_id = False
    
    # FIXME: do we want to handle 'extra'?

    def render(self, field, key, value, REQUEST):
        use_ampm = field.get_value('ampm_time_style')
        hide_day = field.get_value('hide_day')
        calendar_picker = field.get_value('calendar_picker')
        start_day = field.get_value('calendar_start')
        # FIXME: backwards compatibility hack:
        if not hasattr(field, 'sub_form'):
            from StandardFields import create_datetime_text_sub_form
            field.sub_form = create_datetime_text_sub_form()

        if value is None and field.get_value('default_now'):
            value = DateTime()
            
        # Allow subfields to get their values even when default_now is set.
        if REQUEST is not None and \
                   REQUEST.form.has_key(field.generate_subfield_key('year')):
            value = None

        if value is None:
            year = None
            month = None
            day = None
            hour = None
            minute = None
            ampm = None
        else:
            year = "%04d" % value.year()
            month = "%02d" % value.month()
            day = "%02d" % value.day()
            if use_ampm:
                hour = "%02d" % value.h_12()
            else:
                hour = "%02d" % value.hour()
            minute = "%02d" % value.minute()
            ampm = value.ampm()

        input_order = field.get_value('input_order')
        if input_order == 'ymd':
            order = [('year', year),
                     ('month', month),
                     ('day', day)]
        elif input_order == 'dmy':
            order = [('day', day),
                     ('month', month),
                     ('year', year)]
        elif input_order == 'mdy':
            order = [('month', month),
                     ('day', day),
                     ('year', year)]
        result = []
        hidden_day_part = ""
        for sub_field_name, sub_field_value in order:
            if hide_day and (sub_field_name == 'day'):
                dayvalue = sub_field_value
                if dayvalue is None:
                    dayvalue = "01" 
                sub_key = field.generate_subfield_key(sub_field_name)
                sub_field = field.sub_form.get_field(sub_field_name)
                hidden_day_part = sub_field.widget.\
                                  render_hidden(sub_field, sub_key,    
                                                dayvalue, REQUEST)
            else:
                result.append(field.render_sub_field(sub_field_name,
                                                     sub_field_value, REQUEST))
        date_result = string.join(result, field.get_value('date_separator'))

        day_id = field.sub_form.get_field('day').generate_field_html_id("subfield_" + field.id + "_day")
        month_id = field.sub_form.get_field('month').generate_field_html_id("subfield_" + field.id + "_month")
        year_id = field.sub_form.get_field('year').generate_field_html_id("subfield_" + field.id + "_year")

        select_day = ''
        if hidden_day_part:
            date_result += hidden_day_part
        else:
            #get the proper html id
            select_day = 'document.getElementById("'+day_id+'").value = RegExp.$3;'
        calendar_popup = ''
        html_id = field.generate_field_html_id(key)
        if calendar_picker:
            calendar_popup = '&nbsp;' + render_element(
                'button',
                css_class='kupu-button kupu-link-reference calendar-button',
                style='padding: 0px 0px 0px 0px',
                id= html_id + '_calendar',
                title='set date',
                contents=' ') + """<script type="text/javascript">
setTimeout(function(){Calendar.setup({inputField : '%s_hiddeninput',
                ifFormat : '%%Y/%%m/%%d %%%s:%%M %%P',
                showsTime : '%s',
                button : '%s_calendar',
                weekNumbers: false,
                timeFormat: '%s',
                date: (new Date()).setHours(0,0,0,0),
                firstDay: '%s'})},100);</script>"""%(html_id,
                                                 use_ampm and 'I' or 'H',
                                                 field.get_value('date_only') and 'false' or 'true',
                                                 html_id,
                                                 use_ampm and '12' or '24',
                                                 start_day,
)
        if not field.get_value('date_only'):
            time_result = (field.render_sub_field('hour', hour, REQUEST) +
                           field.get_value('time_separator') +
                           field.render_sub_field('minute', minute, REQUEST))

            hour_id = field.sub_form.get_field('hour').generate_field_html_id("subfield_" + field.id + "_hour")
            minute_id = field.sub_form.get_field('minute').generate_field_html_id("subfield_" + field.id + "_minute")
            ampm_id = field.sub_form.get_field('ampm').generate_field_html_id("subfield_" + field.id + "_ampm")
            if use_ampm:
                time_result += '&nbsp;' + field.render_sub_field('ampm',
                                                            ampm, REQUEST)
            calendar_popup += calendar_picker and render_element(
                                'input',
                                type='hidden',
                                id=html_id + '_hiddeninput',
                                onchange='var pattern = /(\d{4})\/(\d{2})\/(\d{2}) (\d{2}):(\d{2}) (am|pm)/; if (pattern.exec(this.value)) { document.getElementById("' + year_id + '").value = RegExp.$1; document.getElementById("' + month_id + '").value = RegExp.$2; ' + select_day + ' document.getElementById("' + hour_id + '").value = RegExp.$4; document.getElementById("' + minute_id + '").value = RegExp.$5; ' + str(use_ampm and 'document.getElementById("' + ampm_id + '").value = RegExp.$6;' or '') + ' }') or ''
            return date_result + '&nbsp;&nbsp;&nbsp;' + time_result + calendar_popup
        else:
            calendar_popup += calendar_picker and render_element(
                                'input',
                                type='hidden',
                                id=html_id + '_hiddeninput',
                                onchange='var pattern = /(\d{4})\/(\d{2})\/(\d{2}) (\d{2}):(\d{2}) (am|pm)/; if (pattern.exec(this.value)) { document.getElementById("' + year_id + '").value = RegExp.$1; document.getElementById("' + month_id + '").value = RegExp.$2; ' + select_day + ' }') or ''
            return date_result + calendar_popup

    def render_hidden(self, field, key, value, REQUEST):
        result = []
        if value is None and field.get_value('default_now'):
            value = DateTime()
        sub_values = {}
        subfields = ['year','month','day']
        if value is not None:
            sub_values['year']  = '%04d' % value.year()
            sub_values['month'] = "%02d" % value.month()
            sub_values['day']   = "%02d" % value.day()
            if not field.get_value('date_only'):
                use_ampm = field.get_value('ampm_time_style')
                subfields.extend(['hour','minute'])
                if use_ampm: subfields.append('ampm')
                if value is not None:
                    if use_ampm:
                        sub_values['hour'] = "%02d" % value.h_12()
                        sub_values['ampm'] = value.ampm()
                    else:
                        sub_values['hour'] = "%02d" % value.hour()
                    sub_values['minute'] = "%02d" % value.minute()
        for subfield in subfields:
            # XXX it would be nicer to pass the hidden value somewhere
            # to the subfields, but ...
            sub_key = field.generate_subfield_key(subfield)
            sub_field = field.sub_form.get_field(subfield)
            result.append(sub_field.widget.render_hidden(sub_field,
                                    sub_key, sub_values.get(subfield), REQUEST))
        return ''.join(result)

    def render_view(self, field, value):
        if value is None:
            return ''

        use_ampm = field.get_value('ampm_time_style')

        year = "%04d" % value.year()
        month = "%02d" % value.month()
        day = "%02d" % value.day()
        if use_ampm:
            hour = "%02d" % value.h_12()
        else:
            hour = "%02d" % value.hour()
        minute = "%02d" % value.minute()
        ampm = value.ampm()

        order = field.get_value('input_order')
        if order == 'ymd':
            output = [year, month, day]
        elif order == 'dmy':
            output = [day, month, year]
        elif order == 'mdy':
            output = [month, day, year]
        date_result = string.join(output, field.get_value('date_separator'))

        if not field.get_value('date_only'):
            time_result = hour + field.get_value('time_separator') + minute
            if use_ampm:
                time_result += '&nbsp;' + ampm
            return date_result + '&nbsp;&nbsp;&nbsp;' + time_result
        else:
            return date_result

DateTimeWidgetInstance = DateTimeWidget()

class LabelWidget(Widget):
    """Widget that is a label only. It simply returns its default value.
    """
    property_names = ['title', 'description',
                      'default', 'css_class', 'hidden', 'extra']

    default = fields.TextAreaField(
        'default',
        title="Label text",
        description="Label text to render",
        default="",
        width=20, height=3,
        required=0)

    def render(self, field, key, value, REQUEST):
        return render_element("div",
                              css_class=field.get_value('css_class'),
                              contents=field.get_value('default'))

    # XXX should render view return the same information as render?
    def render_view(self, field, value):
        return field.get_value('default')

LabelWidgetInstance = LabelWidget()

def render_tag(tag, **kw):
    """Render the tag. Well, not all of it, as we may want to / it.
    """
    attr_list = []

    # special case handling for css_class
    if kw.has_key('css_class'):
        if kw['css_class'] != "":
            attr_list.append('class="%s"' % kw['css_class'])
        del kw['css_class']

    # special case handling for extra 'raw' code
    if kw.has_key('extra'):
        extra = kw['extra'] # could be empty string but we don't care
        del kw['extra']
    else:
        extra = ""

    # handle other attributes
    for key, value in kw.items():
        if value is None:
            if key == 'value':
                value = ''
            else:
                value = key
        attr_list.append('%s="%s"' % (key, html_quote(value)))

    attr_str = string.join(attr_list, " ")
    return "<%s %s %s" % (tag, attr_str, extra)

def render_element(tag, **kw):
    if kw.has_key('contents'):
        contents = kw['contents']
        del kw['contents']
        return "%s>%s</%s>" % (apply(render_tag, (tag, ), kw), contents, tag)
    else:
        return apply(render_tag, (tag, ), kw) + " />"
