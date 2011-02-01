Introduction
============

This is a Plone 4.0 buildout.

Installation
------------

- To install Plone follow these steps::

    $ svn export http://svn.aclark.net/svn/public/plone/branches/4.0.x/ plone
    $ cd plone

- Or, extend this buildout.cfg file in your buildout.cfg file and add the
  appropriate parts, e.g.::

    [buildout]
    extends =
    http://dist.aclark.net/build/plone/4.0.x/buildout.cfg
    extends-cache = .
    parts = plone

- Then::

    $ python2.6 bootstrap.py
    $ bin/buildout
    $ bin/plone fg

- Now open ``http://localhost:8080``.

- Login with:

    - User: admin
    - Password: admin

- Click ``Create Plone site`` to add a Plone site

Have fun! Questions/Comments/Concerns? Email: aclark@aclark.net.
