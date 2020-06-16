.. _new-blog:

Creating a new blog
===================

This section will guide you through the steps required to get a blohg-based
blog up and running.

Make sure that you read all the content available here in order to know how
to use blohg properly.


.. _init:

Initializing the repository
---------------------------

blohg will install a script called ``blohg`` for you. This script is able to
create a new Mercurial (or Git) repository, using the default template and/or
run the development server. It will be your main tool to interact with blohg.

To create a new repository, type::

    $ blohg initrepo --repo-path my_blohg

Where ``my_blohg`` is the directory where the new repository will be created.

Make sure that the directory doesn't exist, or is empty, before try to
initialize the repository.

If you want to use Git instead of Mercurial, type::

    $ blohg initrepo --repo-path my_blohg --git

When the repository is created, do the initial commit::

    $ hg commit -Am 'initial commit'

Or for Git::

    $ git add .
    $ git commit -m 'initial commit'


Repository structure
~~~~~~~~~~~~~~~~~~~~

The repository structure is pretty easy to understand::

    my_blohg/
    |-- config.yaml
    |-- content
    |   |-- about.rst
    |   |-- attachments
    |   |   `-- mercurial.png
    |   `-- post
    |       |-- example-post.rst
    |       `-- lorem-ipsum.rst
    |-- static
    |   `-- screen.css
    `-- templates
        |-- base.html
        |-- post_list.html
        `-- posts.html


+--------------------------+---------------------------------------------------------+
| Directory/File           | Description                                             |
+==========================+=========================================================+
| ``config.yaml``          | The main configuration file.                            |
+--------------------------+---------------------------------------------------------+
| ``content/``             | The main content directory (for pages, posts and        |
|                          | attachments).                                           |
+--------------------------+---------------------------------------------------------+
| ``content/post/``        | The posts directory. Any content stored here is handled |
|                          | as blog post, instead of page.                          |
+--------------------------+---------------------------------------------------------+
| ``content/attachments/`` | The attachments directory. Any images or static         |
|                          | files used in posts and pages should be here.           |
+--------------------------+---------------------------------------------------------+
| ``static/``              | The directory with static files used in the templates,  |
|                          | like CSS files or images.                               |
+--------------------------+---------------------------------------------------------+
| ``templates/``           | The directory with the Jinja2 templates.                |
+--------------------------+---------------------------------------------------------+


.. _configuration:

Configuration options
---------------------

You can heavily change the behavior of blohg by changing some configuration
options.

These are the built-in configuration options for the ``config.yaml`` file:

+----------------------+---------------------------------------------------+-------------------------+
| Configuration option | Description                                       | Default value           |
+======================+===================================================+=========================+
| POSTS_PER_PAGE       | Number of posts per page. Used by the posts       | ``10``                  |
|                      | pagination and the Atom feeds.                    |                         |
+----------------------+---------------------------------------------------+-------------------------+
| POSTS_PER_ATOM_FEED  | Number of posts listed on the Atom feed           | POSTS_PER_PAGE          |
+----------------------+---------------------------------------------------+-------------------------+
| AUTHOR               | The name of the main author of the blog. Used by  | ``'Your Name Here'``    |
|                      | the Atom feeds.                                   |                         |
+----------------------+---------------------------------------------------+-------------------------+
| TAGLINE              | A short tagline for the blog.                     | ``'Your cool tagline'`` |
+----------------------+---------------------------------------------------+-------------------------+
| TITLE                | The title of the blog, without HTML tags.         | ``'Your title'``        |
+----------------------+---------------------------------------------------+-------------------------+
| TITLE_HTML           | The title of the blog, with HTML tags.            | ``'Your HTML title'``   |
+----------------------+---------------------------------------------------+-------------------------+
| CONTENT_DIR          | The directory of the repository where the content | ``content``             |
|                      | is stored.                                        |                         |
+----------------------+---------------------------------------------------+-------------------------+
| TEMPLATES_DIR        | The directory of the repository where the         | ``templates``           |
|                      | templates are stored.                             |                         |
+----------------------+---------------------------------------------------+-------------------------+
| STATIC_DIR           | The directory of the repository where the static  | ``static``              |
|                      | files are stored.                                 |                         |
+----------------------+---------------------------------------------------+-------------------------+
| ATTACHMENT_DIR       | The directory of the repository where the         | ``content/attachments`` |
|                      | attachments are stored.                           |                         |
+----------------------+---------------------------------------------------+-------------------------+
| ROBOTS_TXT           | Enable ``robots.txt``, to prevent search engines  | ``True``                |
|                      | from indexing source files, a.k.a. don't follow   |                         |
|                      | "View Source" hiperlinks.                         |                         |
+----------------------+---------------------------------------------------+-------------------------+
| SHOW_RST_SOURCE      | Enable the view that shows the reStructured text  | ``True``                |
|                      | source of your posts and pages.                   |                         |
+----------------------+---------------------------------------------------+-------------------------+
| POST_EXT             | The extension of your post/page files.            | ``'.rst'``              |
+----------------------+---------------------------------------------------+-------------------------+
| OPENGRAPH            | Enable the `Open Graph`_ meta tags block.         | ``True``                |
+----------------------+---------------------------------------------------+-------------------------+
| EXTENSIONS           | List of enabled extensions.                       | ``[]``                  |
+----------------------+---------------------------------------------------+-------------------------+
| EXTENSIONS_DIR       | The directory of the repository where the         | ``ext``                 |
|                      | extensions are stored.                            |                         |
+----------------------+---------------------------------------------------+-------------------------+
| RST_HEADER_LEVEL     | reStructuredText header level                     | ``3``                   |
+----------------------+---------------------------------------------------+-------------------------+
| THEME                | Defines ``Dark`` or ``Light`` for the main style  | ``Light``               |
|                      | template.                                         |                         |
+----------------------+---------------------------------------------------+-------------------------+

The default values are used if the given configuration key is ommited (or
commented out) from the ``config.yaml`` file.


.. _templates:

Customizing your templates
--------------------------

If you look at the ``my_blohg`` directory you'll see a ``templates`` directory.
It stores some Jinja2_ templates that are used by blohg.

.. _Jinja2: http://jinja.pocoo.org/

Take a look at the Jinja2_ documentation to learn how it works. The default
templates provided by ``blohg initrepo`` are a good start point.

These are the blohg built-in variables globally available for your templates:

+------------------+---------------------------------------------------------+
| Variable         | Description                                             |
+==================+=========================================================+
| ``version``      | A string with the current version.                      |
+------------------+---------------------------------------------------------+
| ``is_post``      | A function with one argument, that returns True if the  |
|                  | given argument is a the path of a post.                 |
+------------------+---------------------------------------------------------+
| ``current_path`` | A string with the path of the current page/post.        |
+------------------+---------------------------------------------------------+
| ``active_page``  | A string with the first piece of the current path,      |
|                  | useful to highlight the menu link for the current page. |
+------------------+---------------------------------------------------------+
| ``tags``         | An iterable with all the available tags, ordered        |
|                  | alphabetically.                                         |
+------------------+---------------------------------------------------------+
| ``config``       | A dictionary with all the configuration options.        |
+------------------+---------------------------------------------------------+


Built-in templates
~~~~~~~~~~~~~~~~~~

These are the built-in templates, that can be overriden from the repository:

404.html
````````

Template for the 404 error page. You don't need to override it on your
Mercurial repository if you don't want to customize something.

.. _posts_html:

_posts.html
```````````

Template with some Jinja2_ blocks that can be used by your custom templates.
If you don't want to use the custom blocks just don't call them from the
templates, and they will be ignored. You don't need to override this file
in the repository.

.. _Disqus: http://disqus.com/
.. _`Open Graph`: http://ogp.me/


These are the custom blocks available:

+---------------+----------------------+---------------------------------------------+
| Type          | Block name           | Where to place                              |
+===============+======================+=============================================+
| Disqus_       | ``disqus_header``    | inside the html header, in ``base.html``.   |
|               +----------------------+---------------------------------------------+
|               | ``disqus_post``      | after the post contents, in ``posts.html``. |
|               +----------------------+---------------------------------------------+
|               | ``disqus_footer``    | at the end of ``base.html``, before the     |
|               |                      | ``</body>`` tag.                            |
+---------------+----------------------+---------------------------------------------+
| Pagination    | ``pagination``       | at the end of ``posts.html``, inside the    |
|               |                      | main ``div``. There's a CSS class, called   |
|               |                      | ``pagination``, to help you when changing   |
|               |                      | the style.                                  |
+---------------+----------------------+---------------------------------------------+
| `Open Graph`_ | ``opengraph_header`` | inside the html header, in ``base.html``    |
+---------------+----------------------+---------------------------------------------+

Disqus_ support depends on the a ``DISQUS`` configuration variable, that should
contain the value of the Disqus_ identifier of your blog. To get it, create an
account at http://disqus.com/.

`Open Graph`_ support depends on a ``OPENGRAPH`` boolean configuration variable,
that defaults to ``True``.


base.html
`````````

The main template file, it's mandatory that this provided in the Mercurial
repository. This template is inherited from by all others.


posts.html
``````````

Template used by the views that show partial/full content of pages and posts.

It inherites from ``_posts.html`` and can make use of its Jinja2_ blocks.

Local variables available for this tempalte:

+------------------+-----------------------------------------------------------+
| Variable         | Description                                               |
+==================+===========================================================+
| ``title``        | A string with the page/post title.                        |
+------------------+-----------------------------------------------------------+
| ``posts``        | A list with all the posts (Metadata objects).             |
+------------------+-----------------------------------------------------------+
| ``full_content`` | A boolean that enables display full content of ``posts``  |
|                  | and not just the abstracts.                               |
+------------------+-----------------------------------------------------------+
| ``pagination``   | A dictionary with 2 items (``num_pages``: number of       |
|                  | pages, and ``current`` current page), used by the         |
|                  | pagination block.                                         |
+------------------+-----------------------------------------------------------+
| ``tag``          | A list of strings with tag identifiers, used by the view  |
|                  | that list posts by tags.                                  |
+------------------+-----------------------------------------------------------+


post_list.html
``````````````

Template for the page with the listing of blog posts, without content, just the
name, the date and the link.

Local variables available for this template:

+------------------+-----------------------------------------------------------+
| Variable         | Description                                               |
+==================+===========================================================+
| ``title``        | A string with the page title (usually "Posts").           |
+------------------+-----------------------------------------------------------+
| ``posts``        | A list with all the posts (Metadata objects).             |
+------------------+-----------------------------------------------------------+


Static files
------------

The ``static/`` directory will store your static files, like CSS_ and images.
You should avoid storing big files inside the Mercurial repository.

.. _CSS: http://www.w3.org/Style/CSS/


Dealing with search engines
---------------------------

blohg will disallow search engines from index your source files (``/source/``
path), creating a ``robots.txt`` file in the root of your blohg instance. If you
isn't running blohg from the root of your domain, you should make the requests
pointing to ``/robots.txt`` redirect to ``/path-to-your-blohg/robots.txt`` in
your webserver configuration.

If you don't want this ``robots.txt`` file, you can just add the following
content to your ``config.yaml`` file:

.. code-block:: yaml

   ROBOTS_TXT: False


Hiding reStructuredText sources
-------------------------------

blohg enables a ``/source/`` endpoint by default, that shows the reStructuredText
source for any post/page of the blog. You can disable it by setting the
``SHOW_RST_SOURCE`` configuration parameter to ``False``. It will raise a 404 error.


Using blohg as a CMS
--------------------

You can use blohg to manage your "static" website, without the concept of blog
posts. Actually the default setup of blohg is already pretty much like a CMS, but
the initial page is a list of posts (or abstracts of posts), and you don't want it
if you don't have blog posts at all.

You can use a static page as the initial page. You just need to save the text
file as ``content/index.rst`` on your repository.

You can also use a static initial page for your blog, if you want, but you'll
need to create a menu link pointing to the page with the list of posts. You can
use the ``views.posts`` endpoint to build it:

.. code-block:: html+jinja

   <a href="{{ url_for('views.posts') }}">Posts</a>


Listing posts by tag
--------------------

Each tag will have its own HTML page with all the posts:

- http://example.org/tag/foo/
- http://example.org/tag/bar/

It is also possible to combine multiple tags and get a HTML page:

- http://example.org/tag/foo/bar/


Atom feeds
----------

blohg generates an Atom_ feed for all the posts and/or tags.

.. _Atom: http://en.wikipedia.org/wiki/Atom_%28standard%29

To include all the posts (actually just the ``POSTS_PER_ATOM_FEED`` last posts),
use the following URL:

http://example.org/atom/

For each tag, use URLs of this form:

- http://example.org/atom/foo/
- http://example.org/atom/bar/

For multiple combined tags, use URLs of this form:

- http://example.org/atom/foo/bar/


Facebook/Google+ integration
----------------------------

We provide Facebook_/`Google+`_ integration using `Open Graph`_ HTML meta-tags.

.. _Facebook: http://www.facebook.com/
.. _`Google+`: http://plus.google.com/

There's a Jinja2_ block available, that will add all the needed property tags
for you. See :ref:`posts_html`.

These are the property tags that will be created:

+-------------+--------------------------------------------------------------+
| Property    | Value                                                        |
+=============+==============================================================+
| title       | ``TITLE`` or the page/post title, if applicable.             |
+-------------+--------------------------------------------------------------+
| description | ``TAGLINE`` or the page/post first paragraph, if applicable. |
|             | Can be overrided by a ``.. description:`` reStructuredText   |
|             | comment.                                                     |
+-------------+--------------------------------------------------------------+
| image       | Full URLs of all the images found in the page/post, if       |
|             | applicable. Each image will have its own ``meta`` tag.       |
+-------------+--------------------------------------------------------------+

If you don't want to use the default block, just remove the block call from
your ``base.html`` template and write your own tags there. Use the default
block, from ``_posts.html``, as reference.

