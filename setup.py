#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    setup.py
    ~~~~~~~~

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import codecs
import re
from setuptools import setup, find_packages
from setuptools.command.install_lib import install_lib as _install_lib

# doing things the wrong way...
# we need the module blohg.version but we can't import the full package
# first time because the dependencies probably aren't solved yet.
import os
import sys
cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cwd, 'blohg'))
from version import version as __version__


# based on code from flask's make-release.py script:
# https://github.com/mitsuhiko/flask/blob/master/scripts/make-release.py
class install_lib(_install_lib):
    """Custom ``install_lib`` phase to patch blohg.version in order to make
    the value calculated on that module permanent for installations. This
    value is usually the hash of a Mercurial changeset, when installing blohg
    from a Mercurial clone."""

    # let's hook our patch at the end of the install phase.
    def install(self):

        # run default install phase
        outfiles = _install_lib.install(self)

        # does nothing if we aren't installing from a live version
        if not re.match(r'^[0-9.]+\+/', __version__):
            return outfiles

        # calculate file path
        path = os.path.join(self.install_dir, 'blohg', 'version.py')

        changed = []

        # helper callback to build the new version string
        def build_version(match):
            changed.append(True)
            return match.group(1) + __version__ + match.group(3)

        # open the file and patch
        with codecs.open(path, encoding='utf-8') as fp:
            contents = re.sub(r"(\s*version\s*=\s*')(.+?)(')(?sm)",
                              build_version, fp.read())

        # if the file was sucessfully patched, save it again
        if changed:
            with codecs.open(path, 'w', encoding='utf-8') as fp:
                fp.write(contents)
        else:
            self.warn('Failed to set version.')

        return outfiles


setup(
    name='blohg',
    version=__version__,
    license='GPL-2',
    description='A Mercurial-based blogging engine',
    long_description=open(os.path.join(cwd, 'README.rst')).read(),
    author='Rafael Goncalves Martins',
    author_email='rafael@rafaelmartins.eng.br',
    url='http://blohg.org/',
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'docutils>=0.8',
        'Flask>=0.8',
        'Flask-Babel>=0.7',
        'Flask-Script>=0.3',
        'Frozen-Flask>=0.7',
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
    cmdclass={'install_lib': install_lib},
    test_suite='blohg.tests.suite',
)
