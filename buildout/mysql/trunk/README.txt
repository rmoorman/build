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

Questions/Comments/Concerns? Email: aclark@aclark.net
