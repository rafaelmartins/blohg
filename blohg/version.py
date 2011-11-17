# -*- coding: utf-8 -*-
"""
    blohg.version
    ~~~~~~~~~~~~~

    Module with the version number related stuff.

    :copyright: (c) 2010-2011 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

# CHANGE ME BEFORE THE RELEASE!
version = '0.8'

# code snippet from sphinx
# http://bitbucket.org/birkenfeld/sphinx/src/tip/sphinx/__init__.py
if '+' in version or 'pre' in version:
    # try to find out the changeset hash if checked out from hg, and append
    # it to version (since we use this value from setup.py, it gets
    # automatically propagated to an installed copy as well)
    try:
        import os
        import subprocess
        cwd = os.path.dirname(os.path.abspath(__file__))
        p = subprocess.Popen(
            ['hg', 'id', '-i', '-R', os.path.join(cwd, '..')],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = p.communicate()
        if out:
            version += '/' + out.strip()
    except Exception:
        pass
