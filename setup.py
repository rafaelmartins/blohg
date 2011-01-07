#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    setup.py
    ~~~~~~~~
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from distutils.command.build import build as _build
from setuptools import setup, find_packages
from setuptools.command.sdist import sdist as _sdist

# doing things the wrong way...
# we need the module blohg.version but we can't import the full package
# first time because the dependencies probably aren't solved yet.
import os, sys
cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cwd, 'blohg'))
from version import version as __version__

cmdclass = dict()
have_babel = True

try:
    from babel.messages import frontend as babel
except ImportError:
    have_babel = False
else:
    cmdclass.update(
        compile_catalog = babel.compile_catalog,
        extract_messages = babel.extract_messages,
        init_catalog = babel.init_catalog,
        update_catalog = babel.update_catalog,
    )


class build(_build):
    def run(self):
        if have_babel:
            self.run_command('compile_catalog')
        _build.run(self)


class sdist(_sdist):
    def run(self):
        if have_babel:
            self.run_command('compile_catalog')
        _sdist.run(self)


cmdclass.update(
    build = build,
    sdist = sdist,
)

setup(
    name = 'blohg',
    version = __version__,
    license = 'GPL-2',
    description = 'A Mercurial-based blog engine',
    long_description = open('README.rst').read(),
    author = 'Rafael Goncalves Martins',
    author_email = 'rafael@rafaelmartins.eng.br',
    url = 'http://labs.rafaelmartins.eng.br/projects/blohg',
    platforms='any',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'docutils>=0.7',
        'Flask>=0.6',
        'Flask-Babel>=0.6',
        'Flask-Script>=0.3',
        'Jinja2>=2.5.2',
        'Mercurial>=1.6',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Natural Language :: Portuguese (Brazilian)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Version Control',
    ],
    data_files = [
        ('share/blohg/config', [
            'share/config/local.py',
            'share/config/remote.py',
        ]),
        ('share/blohg', ['share/blohg.wsgi']),
    ],
    scripts = ['bin/blohg'],
    cmdclass = cmdclass,
)
