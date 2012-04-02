.. _install:

Installing blohg
================

This section will guide you through the alternatives to setup blohg in
your operating system. blohg is currently tested on Linux_ and Windows_,
but should works in any operating system where Flask_ and Mercurial_
runs properly.

blohg works on Python 2.6 and 2.7. 

blohg is available at the *Python Package Index* (PyPI_):

http://pypi.python.org/pypi/blohg

.. _Linux: http://kernel.org/
.. _Windows: http://windows.microsoft.com/
.. _Flask: http://flask.pocoo.org/
.. _Mercurial: http://mercurial.selenic.com/
.. _PyPI: http://pypi.python.org/


Manually
--------

Download the latest tarball from PyPI_, extract it and run::

   # python setup.py install


Using ``pip``/``easy_install``
------------------------------

To install blohg using ``pip``, type::

    # pip install blohg

Or using ``easy_install``, type::

    # easy_install blohg


Gentoo Linux
------------

There's a Gentoo_ ebuild available in the main tree. Install it using::

    # emerge -av www-apps/blohg

.. _Gentoo: http://www.gentoo.org/


Windows
-------

.. _Mercurial: http://mercurial.selenic.com/

You can install blohg easily on Windows using ``pip``/``easy_install``, but
it will try to build the Mercurial C extensions by default, and will fail
if you don't have a compiler installed. You may want to install a compiler,
or just install the pure Python implementations of Mercurial extensions
before install blohg, using something like this inside a directory with
the latest Mercurial_ sources extracted::

    # python setup.py --pure install

