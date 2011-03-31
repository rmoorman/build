Introduction
============

This is a Plone 2.1 buildout. 

Installation
------------

    [buildout]
    extends =
    http://dist.aclark.net/build/plone/2.1.x/buildout.cfg
    extends-cache = .
    parts =
        plone
        instance

- Then::

    $ python2.4 bootstrap.py
    $ bin/buildout
    $ bin/instance fg

- Now open ``http://localhost:8080/manage``.

- Login with:

    - User: admin
    - Password: admin

- Use the `Add` menu in the upper right to add a Plone site.

Have fun! Questions/Comments/Concerns? Email: aclark@aclark.net.
