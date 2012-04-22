.. _deploy:

Deploying your blog
===================

Using a WSGI app
----------------

At this point you should have a Mercurial repository with your blog ready to be
deployed.

Copy it to your remote server as usual. e.g. using ``ssh``::

    $ hg clone my_blohg ssh://user@yourdomain.tld/path/to/my_blohg/

Supposing that your Mercurial repository is ``my_blohg``.

Don't forget to add the remote path to your local ``my_blohg/.hg/hgrc`` [paths]
section.

The blohg deployment process is similar to any other Flask_-powered application.
Take a look at the Flask_ deployment documentation:

.. _Flask: http://flask.pocoo.org/

http://flask.pocoo.org/docs/deploying/

To create your Flask_ ``app`` object, use the following code:

.. code-block:: python

   from blohg import create_app
   application = create_app('/path/to/my_blohg')

There's a sample ``blohg.wsgi`` file (for Apache_ mod_wsgi_) available here:

.. _Apache: http://httpd.apache.org/
.. _mod_wsgi: http://www.modwsgi.org/

http://hg.rafaelmartins.eng.br/blohg/file/tip/share/blohg.wsgi

Using static pages
------------------

.. program:: blohg freeze

You can use the `freeze` command to generate a static version of your
blog. This will create a :file:`build` directory with the content of
your blog as static pages. This way, you can put those pages (via
:command:`ftp`, :command:`rsync`, :command:`hg`, ...) on a static
hosting provider.

.. option:: --serve

   This option will serve your generated pages as a local web
   server. This can be used to check that all links works fine, or
   that all content has been generated.

.. option:: --noindex

   This option will generate your post as html files rather than as
   directories containing a :file:`index.html` file.

.. note::

   This command uses `Frozen-Flask`_ as underlying generator. The
   configuration parameters from Frozen-Flask are also efective for
   this command, just put them inside blohg's :ref:`configuration file
   <configuration>`. One worth mentionning is ``FREEZER_BASE_URL``, as
   it indicates which base url to put in front of the external links,
   like is used for all the attachments.

.. _`Frozen-Flask`: http://packages.python.org/Frozen-Flask/
