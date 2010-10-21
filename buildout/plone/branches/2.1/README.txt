Introduction
============

This is a Plone 2.1 buildout featuring the Plone 2.1 tarball from
http://dist.plone.org/archive.

Install
-------

- To install Plone follow these steps::

    $ svn export http://svn.aclark.net/svn/public/buildout/plone/branches/2.1/ plone
    $ cd plone

- Or, extend the ``buildout.cfg`` file in your buildout and add the
  appropriate parts, e.g.::

    [buildout]
    extends =
    http://dist.aclark.net/buildout/plone/2.1/buildout.cfg
    extends-cache = cache 
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
