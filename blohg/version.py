# -*- coding: utf-8 -*-
"""
    blohg.version
    ~~~~~~~~~~~~~

    Module with the version number related stuff.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import re


# CHANGE ME BEFORE THE RELEASE!
# when this file got installed from a mercurial repository, the hash of the
# current changeset is appended to the 'version' variable.
version = '0.12+'

# the file isn't installed but this isn't a stable release, then we may be
# running from a git repository. let's verify.
if re.match(r'^[0-9.]+\+$', version):

    import os
    import subprocess

    # root dir is where the parent dir of the dir where this file is.
    root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

    # if we are inside a git repository...
    if os.path.isdir(os.path.join(root_dir, '.git')):
        try:
            git_version = subprocess.check_output(['git', 'rev-parse',
                                                   '--short', 'HEAD'])
            # append the changeset hash to the version.
            if git_version:
                version += '/' + git_version.strip()
        except Exception:
            # yeah, it is a bad exception, I know, but I don't want to kill
            # blohg just because I can't parse the git version for some reason
            pass
