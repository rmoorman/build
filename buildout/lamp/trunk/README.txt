Introduction
============

- This is the companion code for the blog entry:
  http://aclark.net/team/aclark/blog/a-lamp-buildout-for-wordpress-and-other-php-apps

- This buildout creates a LAMP stack, suitable for deploying many PHP apps. 

Installation
=============

- To install:

    % svn co https://svn.aclark.net/svn/public/buildout/lamp/trunk lamp-buildout
    % cd lamp-buildout
    % python bootstrap.py
    % bin/buildout
    % bin/supervisord

Questions/Comments/Concerns?

E-mail: aclark@aclark.net
