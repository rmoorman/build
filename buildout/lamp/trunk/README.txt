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
