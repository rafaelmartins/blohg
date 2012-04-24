Writing blog pages/posts
========================

blohg uses the standard reStructuredText_ syntax for pages and posts, with some
additional directives.

.. _reStructuredText: http://docutils.sourceforge.net/rst.html


Tagging posts
-------------

blohg implements the concept of tags for posts. Tags are defined as a
comma-separated list inside a reStructuredText comment in the post source:

.. code-block:: rest

   .. tags: my,cool,tags

Put this comment wherever you want inside the post.


Overriding the creation date
----------------------------

blohg retrieves the creation date of each page and post from the Mercurial
repository, using the date of the first commit of the source file on it. If you
want to override this date, just insire the UNIX timestamp of the desired date
inside a reStructuredText comment:

.. code-block:: rest

   .. date: 1304124215

This is useful if you want to migrate content from another blog.


Overriding the post/page author
-------------------------------

blohg retrieves the author of each post/page from the Mercurial repository,
as it does with the creation date. This data can be used in templates through
the variables ``post.author_name`` and ``post.author_email``. To override
this data, add a reStructuredText comment like this:

.. code-block:: rest
    
    .. author: John <john@example.com>


Post aliases
------------

When migrating from another blogging system or URL structure, you can have 
blohg redirect your readers to the new URL's by providing your posts with URL 
aliases. If you need this, insert a reStructuredText comment with a comma
separated list of the aliases for the post like this:

.. code-block:: rest
    
    .. aliases: /my-old-post-location/,/another-old-location/

By default, blohg will issue a 302 (temporary) redirection. If you want, you
can have blohg issue a 301 (permanent) redirection instead like this:

.. code-block:: rest
    
    .. aliases: 301:/my-old-post-location/,/another-old-location/

The ``301:`` prefix is per URL and must be repeated for every URL you wish
to 301 redirect.


Adding attachments
------------------

You may want to add some images and attach some files to your posts/pages. To
atach a file, just put it in the directory ``content/attachments`` of your
Mercurial repository and use one of the custom reStructuredText_ directives and
roles below in your post/page.

Directive ``attachment-image``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Identical to the ``image`` directive, but loads the image directly from your
``content/attachments`` directory.

Usage example:

.. code-block:: rest

    .. attachment-image:: mercurial.png

Directive ``attachment-figure``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Identical to the ``figure`` directive, but loads the image directly from your
``content/attachments`` directory.

Usage example:

.. code-block:: rest

    .. attachment-figure:: mercurial.png


Interpreted Text Role ``attachment``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Interpreted Text Role that generates a link to the attachment (``reference``
node). You can add a custom label for link after '|'.

Usage example:

.. code-block:: rest

    This is the attachment link: :attachment:`mercurial.png`
    This is the attachment link: :attachment:`mercurial.png|link to file`


Additional reStructuredText directives/interpreted text roles
-------------------------------------------------------------

These are additional custom directives, that add some interesting
functionality to the standard reStructuredText_ syntax.

Directive ``youtube``
~~~~~~~~~~~~~~~~~~~~~

reStructuredText_ directive that creates an embed object to display a video
from YouTube_.

.. _YouTube: http://www.youtube.com/

Usage example:

.. code-block:: rest

    .. youtube:: erPnyi90cIc
       :align: center
       :height: 344
       :width: 425

Directive ``vimeo``
~~~~~~~~~~~~~~~~~~~~~

reStructuredText_ directive that creates an embed object to display a video
from Vimeo_.

.. _Vimeo: http://vimeo.com/

Usage example:

.. code-block:: rest

   .. vimeo:: 2539741
      :align: center
      :height: 344
      :width: 425




Directive ``code``
~~~~~~~~~~~~~~~~~~

reStructuredText_ directive that creates a pre tag suitable for decoration with
http://alexgorbatchev.com/SyntaxHighlighter/

Usage example:

.. code-block:: rest

    .. code:: python

        print "Hello, World!"

    .. raw:: html

        <script type="text/javascript" src="http://alexgorbatchev.com/pub/sh/current/scripts/shCore.js"></script>
        <script type="text/javascript" src="http://alexgorbatchev.com/pub/sh/current/scripts/shBrushPython.js"></script>
        <link type="text/css" rel="stylesheet" href="http://alexgorbatchev.com/pub/sh/current/styles/shCoreDefault.css"/>
        <script type="text/javascript">SyntaxHighlighter.defaults.toolbar=false; SyntaxHighlighter.all();</script>


Directive ``sourcecode``
~~~~~~~~~~~~~~~~~~~~~~~~

reStructuredText directive that does syntax highlight using Pygments.

Usage example:

.. code-block:: rest

    .. sourcecode:: python
       :linenos:

        print "Hello, World!"

The ``linenos`` option enables the line numbering.

To be able to use this directive you should generate a CSS file with the style
definitions, using the ``pygmentize`` script, shipped with Pygments.

::

    $ pygmentyze -S friendly -f html > static/pygments.css

Where ``friendly`` will be your Pygments style of choice.

This file should be included in the main template, usually ``base.html``:

.. code-block:: html+jinja

    <link type="text/css" media="screen" rel="stylesheet" href="{{
        url_for('static', filename='pygments.css') }}" />

This directive is based on ``rst-directive.py``, created by the Pygments authors.


Directive ``math``
~~~~~~~~~~~~~~~~~~

reStructuredText_ directive that creates an image HTML object to display a
LaTeX equation, using Google Chart API.

Usage example:

.. code-block:: rest

    .. math::

        \frac{x^2}{1+x}


Directive ``include``
~~~~~~~~~~~~~~~~~~~~~~~~

reStructuredText_ directive that reads a reStructuredText-formatted text file
and parses it in the current document's context at the point of the directive.
The directive argument is the path to the file to be included, relative to the
repository root.

This directive replaces the ``include`` directive, provided by docutils, that
can be harmful when running on shared environments.

Usage example:

.. code-block:: rest

    .. include:: somefile.txt

More detailed documentation can be viewed in the `Docutils' documentation`__.

__ http://docutils.sourceforge.net/docs/ref/rst/directives.html#id48

This directive, unlike default implementation, will include files stored in
the Mercurial repository.

The directive ``include-hg`` is an alias for this directive.

reStructuredText variables declared as comments in the included files are
going to be ignored.


Directive ``subpages``
~~~~~~~~~~~~~~~~~~~~~~

reStructuredText_ directive that creates a bullet-list with the subpages of
the current page, or of a given page.

Usage example:

.. code-block:: rest

    .. subpages::

Or:

.. code-block:: rest

    .. subpages:: projects

Supposing that you have a directory called ``content/projects`` and some reStructuredText_
files on it. Subdirectories are also allowed.

It is also possible to change the way the bullet-list is sorted, using the
options ``sort-by`` and ``sort-order``:

.. code-block:: rest

    .. subpages::
       :sort-by: slug
       :sort-order: desc

Available options for ``sort-by`` are ``slug`` (default option), ``title``
and ``date``, and for ``sort-order`` are ``asc`` (default option) and
``desc``.

This directive will only show the files from the root of the directory. It's not
recursive.


Interpreted Text Role ``page``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Interpreted Text Role that generates a link to the given page. The
text displayed is by default the title of the linked page. You can
replace it with a custom title using this syntax: ``:page:`Link title
<linked-page>```.

Usage example:

.. code-block:: rest

    This is the :page:`posts/my-first-blog-post`
    This is my :page:`Introduction Post <posts/my-first-blog-post>`

Previewing your post/page
-------------------------

After writing your post/page you will want to preview it in your browser. You
should use the ``blohg`` script to run the development server::

    $ blohg runserver --repo-path my_blohg

Supposing that your Mercurial repository is the ``my_blohg`` directory.

If the blohg script is running on the debug mode, which is the default, it will
load all the uncommited content available on your local copy.

If you disable the debug mode (``--no-debug`` option), it will only load the
content that was already commited. This is the default behavior of the application
when running on the production server.

For help with the script options, type::

    $ blohg runserver -h

Commiting your post/page
------------------------

After finishing your post and previewing it in your browser, commit your
reStructuredText to the repo as usual.

