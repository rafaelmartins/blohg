Upgrading blohg
===============

From <=0.5.1 to 0.6
-------------------

blohg 0.6 introduces support to Flask 0.7, that comes with some backwards
incompatibilities.

You'll need to run the flask-07-upgrade.py_ script inside your blog
repository to fix your templates, as described in the Flask documentation:

.. _flask-07-upgrade.py: https://raw.github.com/mitsuhiko/flask/master/scripts/flask-07-upgrade.py

http://flask.pocoo.org/docs/upgrading/#version-0-7
