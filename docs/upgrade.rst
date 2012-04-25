.. upgrade:

Upgrading blohg
===============

From <=0.5.1
------------

blohg 0.6 introduces support to Flask 0.7, that comes with some backwards
incompatibilities.

You'll need to run the flask-07-upgrade.py_ script inside your blog
repository to fix your templates, as described in the Flask documentation:

.. _flask-07-upgrade.py: https://raw.github.com/mitsuhiko/flask/master/scripts/flask-07-upgrade.py

http://flask.pocoo.org/docs/upgrading/#version-0-7


From <=0.9.2
------------

blohg 0.10 introduces Facebook_/`Google+`_ integration using the
`Open Graph`_ protocol.

.. _Facebook: http://www.facebook.com/
.. _`Google+`: http://plus.google.com/
.. _`Open Graph`: http://ogp.me/

See :ref:`posts_html`, or just add the following content to your ``base.html``
template, inside of the ``<head>`` and ``</head>`` tags:

.. sourcecode:: html+jinja

    <!-- begin opengraph header -->
    {% block opengraph_header %}{% endblock %}
    <!-- end opengraph header -->

blohg 0.10 uses ``jinja2.Markup`` to return HTML content from the models,
deprecating the usage of the ``safe`` filter. You may want to fix your templates:

.. sourcecode:: diff

    --- a/templates/posts.html
    +++ b/templates/posts.html
    @@ -21,9 +21,9 @@
    
     <!-- begin html parsed by docutils -->
     {% if full_content -%}
    -    {{ post.full_html|safe }}
    +    {{ post.full_html }}
     {% else -%}
    -    {{ post.abstract_html|safe }}
    +    {{ post.abstract_html }}
     {%- endif %}
     <!-- end html parsed by docutils -->
    
The directive ``.. include::`` was patched and will just have access to files
from the Mercurial repository for now. This change improves the security,
avoiding the access of files from the host filesystem, and makes it possible to
include files inside the repository. Please remove any calls of this directive
that were using files outside the repository.

