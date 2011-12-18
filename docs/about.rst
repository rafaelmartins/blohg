About blohg
===========

blohg_ is a Mercurial_-based blogging engine written in Python_, built with the
Flask_ micro-framework and some of his available extensions. All the content of
the blogs are stored inside Mercurial_ repositories and the repository history
is used for build the posts and pages. blohg uses Jinja2_ as template engine.

.. _blohg: http://blohg.org/
.. _Mercurial: http://mercurial.selenic.com/
.. _Python: http://python.org/
.. _Flask: http://flask.pocoo.org/
.. _Jinja2: http://jinja.pocoo.org/


Motivation
----------

Everybody knows that we have a big number of blogging engines lying around the
blogosphere, but there's not a lot of choices for programmers, that are used to
work daily with source-code editors and version control systems, and may be more
productive when blogging using these tools, instead of the fancy WYSIWYG_
editors and administration interfaces.

.. _WYSIWYG: http://en.wikipedia.org/wiki/WYSIWYG

Actually this isn't the first project trying to implement a VCS_-based blogging
engine, but most of the existing projects aren't tied to a VCS_ and are just
using text files that can be versioned with a VCS_, without take all his
advantages.

.. _VCS: http://en.wikipedia.org/wiki/Revision_control

This project uses Mercurial_ as VCS_ and reStructuredText_ as markup language.
Both are pretty popular on the Python ecosystem and pretty easy to use.

.. _reStructuredText: http://docutils.sourceforge.net/rst.html

Basic concepts
--------------

These are some of the basic concepts needed to understand how blohg works.
Additionally, you should know how Mercurial works and the reStructuredText
syntax.

Pages
~~~~~

Pages are composed by "static" content, like an "about me" page. They aren't
listed on atom feeds or the home. Pages can be stored in any directory inside
``content/`` in the repository and you need to create the menu entry manually,
inside the template.

Posts
~~~~~

Posts are the dynamic content of a blog. They are shown on the home page and
atom feeds, ordered by publication date descendant. Posts should be stored
inside the directory ``content/post/``. Sub-directories are allowed.

Tags
~~~~

Tags are identifiers that are used to classify posts by subject. Each tag
generates a page and an atom feed with related posts. Tags aren't applicable to
pages.


Repository structure
--------------------

The repository structure is pretty easy to understand::

    blohg/repo_template/
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


- ``config.yaml`` is the main configuration file.
- ``content/`` is the main directory for content (pages, posts and attachments).
  Posts are stored at ``content/post/``, pages are stored anywhere inside
  ``content/`` and attachments are stored at ``content/attachments/``
- ``static/`` is the directory with static files used by your blog, like css
  files or images.
- ``templates/`` is the directory with your Jinja2 templates.


Additional features
-------------------

blohg generates an Atom_ feed for all the posts and/or tags.

.. _Atom: http://en.wikipedia.org/wiki/Atom_%28standard%29

For all the posts (actually just the ``POSTS_PER_PAGE`` last posts), use the
following URL:

http://yourdomain/atom/

For tags, use the following URLs:

- http://yourdomain.com/atom/foo/
- http://yourdomain.com/atom/foo/bar/

The second example will generate an Atom feed for the posts with both tags.
You can use how many tags you want.

There's also a HTML file with the same behavior:

- http://yourdomain.com/tag/foo/
- http://yourdomain.com/tag/foo/bar/

