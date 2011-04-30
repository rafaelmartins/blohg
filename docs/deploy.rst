Deploying your blog
===================

At this point you should have a Mercurial repositor with your blog ready to be
deployed.

Copy it to your remote server as usual. e.g. using ``ssh``::
    
    $ hg clone my_blohg ssh://user@yourdomain.tld/path/to/my_blohg/

Supposing that your Mercurial repository is ``my_blohg``.

Don't forget to add the remote path to your local ``my_blohg/.hg/hgrc`` [paths]
section.

blohg deployment process is similar to any other Flask_-powered application.
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
