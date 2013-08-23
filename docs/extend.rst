Writing extensions
==================

.. warning::

   This feature is experimental and mostly not documented. Use it at your
   own risk. Things may change on the go. You should be ready to look at
   the source code if something breaks.

.. warning::

   This is a last resource feature, that may open a security hole on shared
   environments, if not deployed correctly! Be careful!


Blohg extensions are usual python scripts or modules, that are imported by
blohg itself, and that can change a big part of its behavior.

Extensions can be installed anywhere on your python path (safe for shared
environments) or even inside the blog repository (unsafe for shared
environments).

The script (or package directory) should be named following the convention::

    blohg_$name

For example, the python script that implements the ``foo`` extension would
be called ``blohg_foo.py``.

Extensions can do almost anything, from adding a new view to adding a new
reStructuredText directive to be used in the posts.

Flask_, Werkzeug_ and docutils_ documentation should be quite useful here,
please read them carefully.

.. _Flask: http://flask.pocoo.org/
.. _Werkzeug: http://werkzeug.pocoo.org/
.. _docutils: http://docutils.sourceforge.net/


Simple extension example
------------------------

Save the code bellow as ``blohg_hello.py``, somewhere in your python path:

.. sourcecode:: python

   # -*- coding: utf-8 -*-

   from blohg.ext import BlohgBlueprint, BlohgExtension

   ext = BlohgExtension(__name__)
   hello = BlohgBlueprint('hello', __name__, url_prefix='/hello')

   @hello.route('/')
   def home():
       return 'Hello world!'


   @ext.setup_extension
   def setup_extension(app):
       app.register_blueprint(hello)


Add the following content to your ``config.yaml`` file:

.. sourcecode:: yaml

   EXTENSIONS:
       - hello


And run your development server::

   $ blohg runserver

If everything is ok, you should see a "Hello World", if you point your browser
at http://127.0.0.1:5000/hello/.


Running extensions from repository
----------------------------------

If you want to run an extension from the repository, you should create an ``ext``
(configurable using the ``EXTENSIONS_DIR`` variable in your configuration file)
directory at the root of the repository and place the extensions there. The
extension setup is the same as explained above.

Extensions shipped inside the repository are called "embedded extensions", and
you need to enable them explicitly in your WSGI script, to avoid security
issues. Replace the ``create_app`` call with something like this:

.. sourcecode:: python

   application = create_app('/path/to/your/repository', embedded_extensions=True)

