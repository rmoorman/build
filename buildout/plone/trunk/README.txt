Introduction
============

This is the companion code for the following blog entry:
    - http://aclark.net/Members/aclark/blog/getting-excited-about-plone-3-2

Install
=======

To install Plone via this method, do the following:

    - svn export https://svn.aclark.net/svn/public/buildout/plone/trunk/ plone
    - python2.4 bootstrap.py
    - bin/buildout
    - bin/instance fg
    - Open a browser to http://localhost:8080/manage
    - Login with admin:admin
    - Create a Plone site called 'Plone' from the ZMI drop down menu
    - Open a browser to http://localhost:8080/Plone
    - Have fun!

Bootstrap
=========

This buildout includes a file called bootstrap.py, which requires only
a valid Python interpreter to run. Occasionally, you may want to check:
    - http://svn.zope.org/repos/main/zc.buildout/trunk/bootstrap

for a newer version of this file.

