Writing blog pages/posts
========================

blohg uses the standard reStructuredText_ syntax for pages and posts, with some
additional directives.

.. _reStructuredText: http://docutils.sourceforge.net/rst.html


Tagging posts
-------------

blohg implements the concept of tags for posts. Tags are defined as a
comma-separated list inside a reStructuredText comment:

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
node).

Usage example:

.. code-block:: rest
    
    This is the attachment link: :attachment:`mercurial.png`


Additional reStructuredText directives
--------------------------------------

These are some additional custom directives, that adds some interesting
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

Directive ``source``
~~~~~~~~~~~~~~~~~~~~

reStructuredText_ directive that creates a pre tag suitable for decoration with
http://alexgorbatchev.com/SyntaxHighlighter/

.. warning::

   this directive will be changed to use Pygments in the future versions.

Usage example:

.. code-block:: rest
   
    .. source:: python
      
        print "Hello, World!"
    
    .. raw:: html
        
        <script type="text/javascript" src="http://alexgorbatchev.com/pub/sh/current/scripts/shCore.js"></script>
        <script type="text/javascript" src="http://alexgorbatchev.com/pub/sh/current/scripts/shBrushPython.js"></script>
        <link type="text/css" rel="stylesheet" href="http://alexgorbatchev.com/pub/sh/current/styles/shCoreDefault.css"/>
        <script type="text/javascript">SyntaxHighlighter.defaults.toolbar=false; SyntaxHighlighter.all();</script>


Directive ``math``
~~~~~~~~~~~~~~~~~~

reStructuredText_ directive that creates an image HTML object to display a
LaTeX equation, using Google Chart API.

Usage example:i

.. code-block:: rest
    
    .. math::
    
        \frac{x^2}{1+x}


Previewing your post/page
-------------------------

After write your post/page you will want to preview it in your browser. You
should use the ``blohg`` script to run the development server::
    
    $ blohg runserver --repo-path my_blohg

Supposing that your Mercurial repository is the ``my_blohg`` directory.

If the blohg script is running on the debug mode, that is the default, it will
load all the uncommited stuff available on your local copy.

If you disable the debug mode (``--no-debug`` option), it will just load the
stuff that was already commited. This is the default behavior of the application
when running on the production server.

For help with the script options, type::
    
    $ blohg runserver -h

Commiting your post/page
------------------------

After finish your post and preview it on your browser, feel free to commit your
reStructuredText to the repo as usual.

