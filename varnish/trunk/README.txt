Introduction
============

This is a Plone 3.3.x buildout with Varnish and Supervisor.

Install
=======

* To install Plone follow these steps:

    % svn export http://svn.aclark.net/svn/public/buildout/varnish/trunk plone
    % python2.4 bootstrap.py
    % bin/buildout
    % bin/instance fg

* Open http://localhost:8080

* Login with admin:admin.

Have fun!

Questions/Comments/Concerns? Email: aclark@aclark.net.
