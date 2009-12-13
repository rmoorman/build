
Zenoss Buildout
===============

This is the companion code for the presentation: http://www.slideshare.net/aclark/zenoss-buildout

Installation
============

To run zenoss via this buildout, try the following:

    % svn export http://svn.aclark.net/svn/public/buildout/zenoss/trunk/ zenoss
    % cd zenoss
    % python bootstrap.py
    % bin/buildout
    % bin/supervisord -e debug -n

If everything looks OK, CTRL-C and start in the background:

    % bin/supervisord

Questions/Comments/Concerns? Please email: aclark@aclark.net.
