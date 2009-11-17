Postgres buildout
=================

A supervisor-driven postgresql installation.

Install
-------

% python bootstrap.py
% bin/buildout
% bin/supervisord -e debug -n

If everything looks OK, CTRL-C and restart in the background:

% bin/supervisord
