# -*- coding: utf-8 -*-
"""
    blohg.version
    ~~~~~~~~~~~~~

    Module with the version number related stuff.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import re


# CHANGE ME BEFORE THE RELEASE!
# when this file got installed from a mercurial repository, the hash of the
# current changeset is appended to the 'version' variable.
version = '0.11.1'

# the file isn't installed but this isn't a stable release, then we may be
# running from a mercurial repository. let's verify.
if re.match(r'^[0-9.]+\+$', version):

    # we don't need to care about use mercurial from command-line, because we
    # are GPL already anyway :)
    from mercurial import hg, ui as hgui
    from mercurial.commands import identify
    import os

    # root dir is where the parent dir of the dir where this file is.
    root_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

    # if we are inside a mercurial repository...
    if os.path.isdir(os.path.join(root_dir, '.hg')):

        # create an ui object
        ui = hgui.ui()

        # create the repo object
        repo = hg.repository(ui, root_dir)

        # use the ui stack to get the return value from the 'hg identify'
        # command, and run the command itself.
        ui.pushbuffer()
        identify(ui, repo, id=True)
        rv = ui.popbuffer()

        # append the changeset hash to the version.
        if rv:
            version += '/' + rv.strip()
