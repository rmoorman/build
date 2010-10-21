Introduction
============

This is a Plone 3.x buildout. You can use it in your buildout via the extends
parameter, e.g.::

    [buildout]
    extends = http://https://svn.aclark.net/svn/public/buildout/plone/branches/3.x/buildout.cfg

Or follow the install instructions below.

Install
=======

- To install Plone 3.x follow these steps::

    $ svn export http://svn.aclark.net/svn/public/buildout/plone/branches/3.x/ plone
    $ python2.4 bootstrap.py
    $ bin/buildout
    $ bin/instance fg

- Login with admin:admin

- Use the `Add` menu to add a Plone site

Have fun! 

Questions/Comments/Concerns? Please email: aclark@aclark.net.
