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
    $ cp -r ``sys.prefix``/share/blohg/config.yaml .
    $ mkdir {content,static,templates}
    $ $EDITOR config.yaml

Change the configuration values as you want. The variables are pretty
obvious and the sample file comes with some useful examples.

The templates (``templates/`` directory) are handled using Jinja2_. Please
take a look at my blog repository for an example of how templates are
handled. (TODO: expand this)

.. _Jinja2: http://jinja.pocoo.org/

http://hg.rafaelmartins.eng.br/rafaelmartins.eng.br/

blohg uses a custom Jinja2_ template loader, that's able to load templates
directly from the Mercurial repository.

The ``static/`` directory should be used for static files. You should
avoid store big files inside the repository.

::

    $ mkdir content/post
    $ cat << EOF > content/post/hello_world.rst
    Hello World!
    ============

    .. tags: hello_world,my_cool_tag
    
    Hello, blohg!
    
    EOF
    $ blohg runserver

Make sure that you run the ``blohg`` script from the root of your local
repository.

If you're lucky, you should get your blog at http://localhost:5000/ ::

    $ hg commit -Am 'initial commit'

Now copy your repository for the remote server as you want.

When your repository is available on the web server, configure your push
path::
    
    $ cat << EOF > .hg/hgrc
    [paths]
    default = https://your_user@example.com/my_blohg/
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

Have fun! :)


Important notes about writing posts/pages
-----------------------------------------

Tags are handled from a reSTructuredText comment: ``.. tags:``. Tags are
comma-separated.

Static pages will not handle tags, then you don't need the ``.. tags:``
comment.


Enjoy!
