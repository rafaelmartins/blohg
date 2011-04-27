Introduction
============


Motivation
----------

Everybody knows that we have a big number of blogging engines lying around the
blogosphere, but there's not a lot of choices for programmers, that are used to
work daily with source-code editors and version control systems, and may be more
productive when blogging using these tools, instead of the fancy WYSIWYG editors
and graphical administration interfaces.

Actually this isn't the first project trying to implement a VCS-based blogging
engine, but most of the existing projects aren't tied to a VCS and are just using
text files that can be versioned with a VCS, without take all his advantages.

This project uses Mercurial as VCS and reStructuredText as markup language. Both
are very popular on the Python ecosystem and pretty easy to use.


Basic concepts
--------------

These are some of the basic concepts needed to understand how blohg works.
Additionally, you should know how Mercurial works and the reStructuredText syntax.

Pages
~~~~~

Pages are composed by "static" content, like an "about me" page. They aren't
listed on atom feeds or the home. Pages can be stored in any directory inside
``content/`` in the repository and you need to create the menu entry manually,
inside the template.

Posts
~~~~~

Posts are the dynamic content of a blog. They are shown on the home page and atom
feeds, ordered by publication date descendant. Posts should be stored inside the
directory ``content/post/``. Sub-directories are allowed.

Tags
~~~~

Tags are identifiers that are used to classify posts by subject. Each tag generates
a page and an atom feed with related posts. Tags aren't applicable to pages.