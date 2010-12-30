[buildout]
extensions = mr.developer
auto-checkout = Products

# A buildout is made of parts.
# For more information on this step and configuration options see:
# http://pypi.python.org/pypi/zc.buildout
parts = 
    zope2
    instance1

[env]
# Get a hold of the current PATH environment variable.
# For more information on this step and configuration options see:
# http://pypi.python.org/pypi/gocept.recipe.env
recipe = gocept.recipe.env

[sources]
Products = svn http://dev.zenoss.org/svn/branches/zenoss-2.3.x/Products

[zope2]
# Install Zope 2.
# For more information on this step and configuration options see:
# http://pypi.python.org/pypi/plone.recipe.zope2install
recipe = plone.recipe.zope2install
url = http://www.zope.org/Products/Zope/2.8.8/Zope-2.8.8-final.tgz

[instance1]
# Create a Zope 2 instance.
# For more information on this step and configuration options see:
# http://pypi.python.org/pypi/plone.recipe.zope2instance
recipe = plone.recipe.zope2instance
zope2-location = ${zope2:location}
user = admin:admin
http-address = 8080
debug-mode = on
verbose-security = on
eggs = 
    simplejson
    twisted
    uuid
    MySQL-Python

products = 
    ${buildout:directory}/products
