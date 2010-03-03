MySQL Buildout
==============

- Need MySQL in your buildout? Try adding this to your [buildout] section:

    --------------
    extends = https://svn.aclark.net/svn/public/buildout/mysql/trunk/buildout.cfg
    parts +=
        env
        grp
        mysql
        mysql-conf
        database
        script-mysql
        script-admin
        pidproxy
    --------------

- A word of caution: remove or comment everything in /etc/mysql/my.cnf before
  using this buildout! If MySQL finds this file (and it will look for
  it) then bad things happen.

Questions/Comments/Concerns? Email: aclark@aclark.net
