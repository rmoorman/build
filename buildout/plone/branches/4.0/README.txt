Introduction
============

This is a Plone 4.x buildout.

Install via export
------------------

- To install Plone, follow these steps::

    $ svn export https://svn.aclark.net/svn/public/buildout/plone/trunk/ plone
    $ python2.6 bootstrap.py
    $ bin/buildout
    $ bin/instance fg

- Open http://localhost:8080

- Login with admin:admin.


Install via extends
-------------------

- Or, extend this buildout.cfg file in your buildout.cfg file, and add the
  appropriate parts, e.g.::

    [buildout]
    extends =
    http://svn.aclark.net/svn/public/buildout/plone/trunk/buildout.cfg
    extends-cache = cache
    parts =
        instance

Have fun!

Questions/Comments/Concerns? Email: aclark@aclark.net.
