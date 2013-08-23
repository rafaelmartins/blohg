.. _about:

About blohg
===========

blohg_ is a Mercurial_ (or alternatively Git_) based blogging engine written in
Python_, built on the top of the Flask_ micro-framework and some of its extensions.
All the content of the blogs are stored inside a repository, and its history
is used to build the posts and pages.

.. _blohg: http://blohg.org/
.. _Mercurial: http://mercurial.selenic.com/
.. _Git: http://git-scm.com/
.. _Python: http://python.org/
.. _Flask: http://flask.pocoo.org/


Motivation
----------

Everybody knows that we have a large number of blogging engines lying around the
blogosphere, but there are not a many choices for programmers, who are used to
working daily with source-code editors and version control systems and may be more
productive when blogging using these tools, instead of the fancy WYSIWYG_
editors and administration interfaces.

.. _WYSIWYG: http://en.wikipedia.org/wiki/WYSIWYG

Actually this isn't the first project trying to implement a VCS_-based blogging
engine, but most of the existing projects aren't tied to a VCS_ and are just
using text files that can be versioned with a VCS_, without taking full
advantage of the VCS's revision history.

.. _VCS: http://en.wikipedia.org/wiki/Revision_control

This project uses Mercurial_ as the VCS_, reStructuredText_ as the markup
language and Jinja2_ as the template engine. All of these are pretty popular
within the Python ecosystem and easy to use.

.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Jinja2: http://jinja.pocoo.org/


Basic concepts
--------------

Here are some of the basic concepts needed to understand how blohg works:
In addition, you should know how Mercurial_ works, the reStructuredText_
syntax and the Jinja2_ syntax.

Pages
~~~~~

Pages are static content, such as an "About me" page. They aren't listed in atom
feeds or in the home view.  You may want to create a menu entry
manually in the template to them.  Pages are ``.rst`` files stored in any directory
inside ``content/``, excluding ``content/post/``. Sub-directories are allowed.

Posts
~~~~~

Posts are the dynamic content of a blog. They are shown on the home page and
atom feeds, ordered by publication date, descendant. Posts should be stored
inside the directory ``content/post/``. Sub-directories are allowed.

Tags
~~~~

Tags are identifiers that are used to classify posts by topic. Each tag
generates a HTML page and an atom feed with related posts. Tags aren't
allowed in pages, only posts.


Main features
-------------

These are some of the cool features of blohg:

.. _CMS: http://en.wikipedia.org/wiki/Content_management_system

- Support for static pages and posts.
- Support for tags for posts.
- Support for aliases, making it easy to migrate from some other blogging engine.
- Support for building a static version of the blog, to host it in restricted
  environments.
- Post/page metadata grabbed from the Mercurial_ repository.
- Plenty of reStructuredText_ directives available, to make the blogging
  experience as smooth as possible.
- Easily customizable by Jinja2_ templates.
- Can be used as a full-featured CMS_.
- Support for pagination for posts.
- Atom feeds for posts and tags.
