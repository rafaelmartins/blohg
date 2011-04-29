Installing blohg
================

These are some of the ways to install blohg at your system. blohg isn't
currently tested in any operating system but Linux_, but should works properly
in anything capable to run Flask_ powered application.

blohg is available at the *Python Package Index* (PyPI_):

http://pypi.python.org/pypi/blohg

.. _Linux: http://kernel.org/
.. _Flask: http://flask.pocoo.org/
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

There's a Gentoo_ ebuild available at the ``gentoo-x86`` tree. Install it
using::
    
    # emerge -av www-apps/blohg

.. _Gentoo: http://www.gentoo.org/

