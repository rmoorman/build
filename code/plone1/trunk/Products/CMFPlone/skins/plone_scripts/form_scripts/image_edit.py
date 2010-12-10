## Script (Python) "image_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=precondition='', file='', id='', title=None, description=None
##title=Edit an image
##

isIDAutogenerated=context.isIDAutoGenerated
original_id=context.getId()

# if there is no id or an autogenerated id, use the filename as the id
# if not id or context.isIDAutoGenerated(id):
# if there is no id, use the filename as the id

filename=getattr(file,'filename', '')
if file and filename and isIDAutogenerated(original_id):
    if not id:
        id = filename[max( string.rfind(filename, '/')
                       , string.rfind(filename, '\\')
                       , string.rfind(filename, ':') )+1:]

    file.seek(0)

# if there is no id specified, keep the current one
# if we already have a non-autogenerated id - it may
# be in use.. we will keep the current id.
if not id:
    id = original_id

new_context = context.portal_factory.doCreate(context, id)

new_context.plone_utils.contentEdit( new_context
                                   , id=id
                                   , description=description )

new_context.edit( precondition=precondition
                , file=file )

return ('success', new_context, 
        {'portal_status_message' : context.REQUEST.get('portal_status_message',
                                                       'Image changes saved.')})

