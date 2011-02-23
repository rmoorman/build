
Wordpress buildout
==================

This is a Wordpress buildout that downloads and extracts the Wordpress tarball.

To use it, do this::

    $ svn export http://svn.aclark.net/svn/public/buildout/wordpress/trunk wp-buildout
    $ cd wp-buildout

Edit the settings in `templates/wp-config-sample.php` and then::

    $ python bootstrap.py
    $ bin/buildout

Now point your Apache with PHP to `wp-buildout/parts/wordpress`, e.g. create
a Directory entry like this::

    <Directory /var/www/wp-buildout/parts/wordpress/>
        Options Indexes FollowSymLinks MultiViews
        AllowOverride None
        Order allow,deny
        allow from all
    </Directory>

Have fun!

Questions/comments/concerns? Email: aclark@aclark.net.
