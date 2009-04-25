Introduction
============

This is a buildout to create a LAMP stack.

For more information, please see:
    - http://aclark.net/Members/aclark/blog/a-lamp-buildout-for-wordpress-and-other-php-apps


References
==========

Buildout:
    - http://pypi.python.org/pypi/zc.buildout/1.2.1

LAMP Stack:
    - http://en.wikipedia.org/wiki/LAMP_(software_bundle)


Install
=======

To install, do the following:
    $ svn co https://svn.aclark.net/svn/public/buildout/lamp/trunk lamp
    $ cd lamp
    $ python bootstrap.py
    $ bin/buildout

Go get coffee, then:
    $ bin/supervisord -e debug -n

If everything looks good:
    $ bin/supervisord


Configure
=========

You can change the default ports by editing buildout.cfg:

    [ports]
    …
    supervisor = 9001
    apache = 8080
    mysql = 3306

Then rerun buildout:
    $ bin/buildout


Virtual Hosting
===============

You can run numerous, isolated PHP environments by proxying
from a web server running on port 80 to the buildout's 
Apache. If you are using Apache on port 80, this can be done 
with mod_proxy_html:
    - http://apache.webthing.com/mod_proxy_html/


