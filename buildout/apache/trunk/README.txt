Apache Buildout
===============

A supervisor-driven buildout for apache.

Installation
============

To install apache via this buildout, try the following:

    % svn export http://svn.aclark.net/svn/public/buildout/apache/trunk apache
    % python bootstrap.py
    % bin/buildout
    % bin/supervisord -e debug -n

If everything looks ok, CTRL-C and run in the background:

    % bin/supervisord

(Stop with bin/supervisorctl shutdown)

Questions/Comments/Concerns? Please email: aclark@aclark.net.

