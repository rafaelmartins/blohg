.. _install:

Installing blohg
================

This section will guide you through the alternatives for setting up blohg in
your operating system. blohg is currently tested on Linux_ and Windows_,
but should works in any operating system where Flask_ and Mercurial_ (and/or
Git_) run properly.

blohg works on Python 2.7.

blohg is available at the *Python Package Index* (PyPI_):

http://pypi.python.org/pypi/blohg

.. _Linux: http://kernel.org/
.. _Windows: http://windows.microsoft.com/
.. _Flask: http://flask.pocoo.org/
.. _Mercurial: http://mercurial.selenic.com/
.. _Git: http://git-scm.com/
.. _PyPI: http://pypi.python.org/

.. warning::

   Before installing blohg manually or using ``pip``, make sure that you have
   a C compiler and the usual build tools (e.g the ``build-essential`` package
   for Debian/Ubuntu) installed. You can work around these dependencies if you
   need (e.g when running Windows), installing Mercurial with ``--pure``
   argument, running the following command inside of a directory with the
   Mercurial sources::

       # python setup.py --pure install

   There's no way to install Git bindings without a compiler, unfortunately.

.. warning::

   libgit2 is experimental and breaks the ABI every minor release. You may have
   some trouble when trying to get pygit2 working.


Manually
--------

Download the latest tarball from PyPI_, extract it and run::

    # python setup.py install


Using ``pip``
-------------

To install blohg using ``pip``, type::

    # pip install blohg

If you want to use Git_ repositories, install a recent version of libgit2_
(yeah, setuptools/distutils don't know how to handle non-python dependencies.
see the official documentation for instructions about how to install it on
your operating system), and type::

    # pip install blohg[git]

.. _libgit2: http://libgit2.github.com/

For ubuntu users, I recommend installing ``libgit2-dev`` package from this PPA:

https://launchpad.net/~xav0989/+archive/libgit2

You should be careful about the version of libgit2 installed on your system.
The major and minor versions of pygit2 should match the major and minor versions
of libgit2, e.g. if the required version of pygit2 is 0.18.1, you need
libgit2-0.18.*.


Gentoo Linux
------------

There's a Gentoo_ ebuild available in the main tree. Install it using::

    # emerge -av www-apps/blohg

.. _Gentoo: http://www.gentoo.org/

