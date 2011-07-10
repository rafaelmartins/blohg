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

Do the initial commit::

    $ hg commit -Am 'initial commit'

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

Template for the 404 error page. There's an useful default file provided by
blohg. You don't need to put it on your Mercurial repository if you don't want
to customize something.

_posts.html
~~~~~~~~~~~

Template with some Jinja2_ blocks that can be used by ``base.html`` and
``posts.html``. You SHOULDN'T provide this file in your repository, if you want
to use these blocks. If you don't want to use them, just rename your
``posts.html`` file to ``_posts.html`` and they will be ignored.

.. _Disqus: http://disqus.com/

- Jinja2_ blocks for Disqus_ comments:

  - ``disqus_header``: place it inside the html header in ``base.html``.
  - ``disqus_post``: place it after the post contents in ``posts.html``.
  - ``disqus_footer``: place it at the end of your html, but before the
    ``</body>`` tag, in ``base.html``.

- Jinja2_ blocks for pagination:

  - ``pagination``: place it at the end of the ``posts.html`` file, but inside
    your main ``div``. There's a CSS class ``pagination`` to help you changing
    the style.

Disqus_ support depends on the ``DISQUS`` configuration variable, that should
contain the value of the Disqus_ identifier of your blog. To get it, create an
account at http://disqus.com/.

base.html
~~~~~~~~~

The main template file, it's mandatory to be provided by the Mercurial
repository. This template is inherited by all the other ones.

posts.html
~~~~~~~~~~

Template used by the views that show partial/full content of pages and posts.

It's inherited by ``_posts.html`` and can make use of his Jinja2_ blocks.

Local variables available for this tempalte:

- ``title``: string with the page/post title.
- ``posts``: list with all the posts (Metadata objects).
- ``full_content``: boolean that enable display full content of ``posts`` and
  not just the abstracts.
- ``pagination``: dictionary with 2 items (``num_pages``: number of pages, and
  ``current``: current page), used by the pagination block.
- ``tag``: list of strings with tag identifiers, used by the view that list
  posts by tags.


post_list.html
~~~~~~~~~~~~~~

Template for the page with the listing of blog posts, without content, just the
name, the date and the link.

Local variables available for this template:

- ``title``: string with the page title (usually "Posts").
- ``posts``: list with all the posts (Metadata objects).


Static files
------------

The ``static/`` directory will store your static files, like CSS_ and images.
You should avoid store big files inside the Mercurial repository.

.. _CSS: http://www.w3.org/Style/CSS/


``robots.txt``
--------------

blohg will disallow search engines from index your source files (``/source/``
path), creating a ``robots.txt`` file at the root of your blohg instance. If you
isn't running blohg from the root of your domain, you should make the requests
pointing to ``/robots.txt`` redirect to ``/path-to-your-blohg/robots.txt`` in
your webserver configuration.

If you don't want this ``robots.txt`` file, you can just add the following
content to your ``config.yaml`` file:

.. code-block:: yaml

   ROBOTS_TXT: False

