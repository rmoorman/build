This is the companion code for the presentation:
    - http://www.slideshare.net/aclark/zenoss-buildout

XXX This is currently in development and not working properly yet,
    but a stable buildout is coming Real Soon Now(TM).

    If you'd like to experiment with the status quo, please try
    the following:

    - svn export http://svn.aclark.net/svn/public/buildout/zenoss/trunk/ zen
    - cd zen
    - python bootstrap.py
    - bin/buildout
    - bin/instance fg

    You should get a traceback on 'rrdtool'.

Questions/Comments/Concerns/WantToHelp?
    - Please email: aclark@aclark.net
