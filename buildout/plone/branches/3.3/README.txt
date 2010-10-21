Introduction
============

This is a Plone 3.3 buildout. 

Install
-------

- To install Plone follow these steps::

    $ svn export http://svn.aclark.net/svn/public/buildout/plone/branches/3.3/ plone
    $ cd plone

- Or, extend this buildout.cfg file in your buildout.cfg file and add the
  appropriate
  parts, e.g.::

    [buildout]
    extends =
    http://dist.aclark.net/buildout/plone/3.3/buildout.cfg
    extends-cache = cache
    parts =  
        zope2
        instance

- Then::

    $ python2.4 bootstrap.py
    $ bin/buildout
    $ bin/instance fg

- Now open ``http://localhost:8080/manage``.

- Login with:

    - User: admin
    - Password: admin

- Use the `Add` menu in the upper right to add a Plone site

Have fun! Questions/Comments/Concerns? Email: aclark@aclark.net.
