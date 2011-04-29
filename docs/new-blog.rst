Creating a new blog
===================

blohg will install a script called ``blohg`` for you. This script is capable to
create a new Mercurial repository for you, using the default template and/or
run the development server. It will be your main tool to interact with blohg.


Initializing the repository
---------------------------

To create a new repository, type::
    
    $ blohg initrepo --repo-path my_blohg

Where ``my_blohg`` is the directory where the template will be installed.

Make sure that the directory doesn't exists, or is empty, before try to
initialize the repository.


Configuring your blog
---------------------

The configuration file is ``config.yaml`` at the root of your repository. It's
an usual YAML_ file with pretty obvious variables names. Edit it as needed.

.. _YAML: http://www.yaml.org/

Customizing your templates
--------------------------

If you look at the ``my_blohg`` directory you'll see a ``templates`` directory.
It stores some Jinja2_ templates that are used by blohg.

.. _Jinja2: http://jinja.pocoo.org/

Take a look at the Jinja2_ documentation to learn how it works. The default
templates provided by ``blohg initrepo`` are a good start point.

These are the variables globally available for your templates:

- ``version``: string with the current version.
- ``is_post``: lambda function, with one argument, that returns True if the
  given argument is a string with the path of a post.
- ``current_path``: returns a string with the path of the current page/post.
- ``active_page``: returns a string with the first piece of the current path,
  useful to highlight the menu link for the current page.
- ``tags``: a list with all the available tags, ordered alphabetically.
- ``config``: a dictionary with all the configuration options.

Here is a list of templates needed by blohg and what each one does.

404.html
~~~~~~~~

TODO

_posts.html
~~~~~~~~~~~

TODO

base.html
~~~~~~~~~

The main template file, it's mandatory to be provided by the Mercurial
repository. This template is inherited by all the other ones.

posts.html
~~~~~~~~~~

Template called by the views that show partial/full content of pages and posts.
Gets a list of posts (``posts``) and should handle them properly.i

TODO

post_list.html
~~~~~~~~~~~~~~

TODO


Static files
------------

The ``static/`` directory will store your static files, like CSS_ and images.
You should avoid store big files inside the Mercurial repository.

.. _CSS: http://www.w3.org/Style/CSS/

