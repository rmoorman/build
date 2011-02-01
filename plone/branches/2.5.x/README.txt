Introduction
============

This is a Plone 2.5 buildout.

Install
-------

- To install Plone follow these steps::

    $ svn export http://svn.aclark.net/svn/public/plone/branches/2.5.x/ plone
    $ python2.4 bootstrap.py
    $ bin/buildout
    $ bin/instance fg

- Or, extend this buildout.cfg file in your buildout.cfg file and add the appropriate
  parts, e.g.::

    [buildout]
    extends =
    http://dist.aclark.net/build/plone/2.5.x/buildout.cfg
    extends-cache = .
    parts = 
        zope2
        instance

- Now open ``http://localhost:8080/manage``.

- Login with:

    - User: admin
    - Password: admin

- Use the `Add` menu in the upper right to add a Plone site

Have fun! Questions/Comments/Concerns? Email: aclark@aclark.net.
