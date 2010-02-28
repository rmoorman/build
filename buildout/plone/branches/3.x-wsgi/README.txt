Introduction
============

This is a buildout for Plone 3.x with WSGI support from repoze.zope2.

Install
=======

- To install Plone follow these steps:

    $ svn export https://svn.aclark.net/svn/public/buildout/plone/branches/3.x-wsgi plone
    $ python2.4 bootstrap.py
    $ bin/buildout
    $ bin/paster serve etc/zope2.ini

- Open http://localhost:8080/Plone

- Login with admin:admin.

Have fun!

Questions/Comments/Concerns? Email: aclark@aclark.net.
