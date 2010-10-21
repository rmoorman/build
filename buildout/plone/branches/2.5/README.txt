Introduction
============

This is a Plone 2.5.x buildout.

Install
=======

- To install Plone, follow these steps::

    $ svn export https://svn.aclark.net/svn/public/buildout/plone/branches/2.5.x/ plone
    $ python2.4 bootstrap.py
    $ bin/buildout
    $ bin/instance fg

- Or, extend this buildout.cfg file in your buildout.cfg file and add the appropriate
  parts, e.g.::

    [buildout]
    extends =
    http://svn.aclark.net/svn/public/buildout/plone/branches/2.5.x/buildout.cfg
    extends-cache = cache
    parts = 
        zope2
        instance

- Open http://localhost:8080/manage

- Login with admin:admin.

- Add a Plone site.

Have fun!


Questions/Comments/Concerns? Email: aclark@aclark.net.
