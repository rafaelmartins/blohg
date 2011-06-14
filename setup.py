#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    setup.py
    ~~~~~~~~

    :copyright: (c) 2010-2011 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from setuptools import setup, find_packages

# doing things the wrong way...
# we need the module blohg.version but we can't import the full package
# first time because the dependencies probably aren't solved yet.
import os
import sys
cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cwd, 'blohg'))
from version import version as __version__

setup(
    name='blohg',
    version=__version__,
    license='GPL-2',
    description='A Mercurial-based blog engine',
    long_description=open(os.path.join(cwd, 'README.rst')).read(),
    author='Rafael Goncalves Martins',
    author_email='rafael@rafaelmartins.eng.br',
    url='http://blohg.org/',
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'docutils>=0.7',
        'Flask>=0.6',
        'Flask-Babel>=0.6',
        'Flask-Script>=0.3',
        'Jinja2>=2.5.2',
        'Mercurial>=1.6',
        'PyYAML',
        'Pygments',  # TODO: make this dependency optional
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Version Control',
    ],
    data_files=[
        ('share/blohg', ['share/blohg.wsgi']),
    ],
    scripts=['bin/blohg'],
)
