Introduction
============

* This is the companion code for the blog entry: http://aclark.net/Members/aclark/blog/getting-excited-about-plone-3-2

Install
=======

* To install the latest Plone via this method, follow these steps:
    - % svn export https://svn.aclark.net/svn/public/buildout/plone/trunk/ plone
    - % python2.4 bootstrap.py
    - % bin/buildout
    - % bin/instance fg
    - Open http://localhost:8080/Plone
    - Login with admin:admin.

Install (WSGI)
==============

* This branch has been modified to work with repoze.zope2.

* To install the latest Plone via this method, follow these steps:
    - % svn export https://svn.aclark.net/svn/public/buildout/plone/branches/repoze/ plone
    - % python2.4 bootstrap.py
    - % bin/buildout
    - % bin/paster serve etc/instance-wsgi.ini
    - Open http://localhost:8080/Plone
    - Login with admin:admin.

Have fun!

Questions/Comments/Concerns? Please email: aclark@aclark.net.
