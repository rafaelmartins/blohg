blohg
~~~~~

blohg is a simple and easy to use blog engine, that uses the Mercurial
SCM as backend, to store the content of the post and pages.

blohg doesn't have a nice control panel nor WYSIWIG editors. All the
content is written using any text editor and reStructuredText with some
custom directives (undocumented yet, please read the docstrings for 
reference).


Starting your blog
------------------

.. warning::
    
    The ``sys.prefix`` on the examples means the prefix value for your
    current environment (the current value of ``sys.prefix``) and not
    the python variable itself, obviously.

::

    $ hg init my_blohg
    $ cd my_blohg
    $ cp -r ``sys.prefix``/share/blohg/config .
    $ $EDITOR config/remote.py

Change the configuration values as you want. The variables are pretty
obvious and the sample file comes with some useful examples. ::

    $ mkdir -p txt/en-us/post
    $ cat << EOF > txt/en-us/post/hello_world.rst
    .. title: Hello World!
    .. tags: hello_world,my_cool_tag
    
    Hello, blohg!
    
    EOF
    $ blohg run

Make sure that you run the ``blohg`` script from the root of your local
repository.

If you're lucky, you should get your blog at http://localhost:5000/ ::

    $ hg commit -A

.. warning::
    
    Make sure you add the ``config/*.pyc`` files to your ``.hgignore`` file

Now copy your repository for the remote server as you want.

When your repository is available on the web server, configure your push
path::
    
    $ cat << EOF > .hg/hgrc
    [paths]
    default = http://your_user@example.com/my_blohg/
    EOF
    $ hg push

.. warning::
    
    This example DOESN'T cover the Mercurial server configuration!


Deploying your blog (using Apache/mod_wsgi)
-------------------------------------------

::
    
    $ cp ``sys.prefix``/share/blohg/blohg.wsgi /some/place/
    $ $EDITOR /some/place/blohg.wsgi

Read the file and change what you need.

Edit your apache configuration and add something like this::
    
    <VirtualHost *:80>
        ServerName example.com
        WSGIScriptAlias / /some/place/blohg.wsgi
    </VirtualHost>

You'll need to add 2 hooks to your remote repository, to update your
working directory and reload your Apache processes every time you commit
some new page/post::

    [hooks]
    changegroup = hg update >&2
    changegroup.apache = touch /some/place/blohg.wsgi

Add this to the ``.hg/hgrc`` file from your remote repository.

Have fun! :)


Important notes about writing posts/pages
-----------------------------------------

Make sure that you always have a ``.. title:`` comment at the begin of
your ``.rst`` file, this is your title!

Static pages will not handle tags, then you don't need the ``.. tags:``
comment. Tags are comma-separated.


Enjoy!
