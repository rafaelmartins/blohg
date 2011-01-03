# -*- coding: utf-8 -*-
"""
    blohg.script
    ~~~~~~~~~~~~
    
    Module with the CLI script related stuff.
    
    :copyright: (c) 2010-2011 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os, sys
from flaskext.script import Server, Manager

from blohg import create_app


def create_script(repo_path):
    """Script object factory
    
    :param repo_path: the path to the mercurial repository.
    :return: the script object (Flask-Script' Manager instance).
    """
    
    if not os.path.exists(os.path.join(repo_path, '.hg')):
        print >> sys.stderr, 'error: invalid Mercurial repository!'
        sys.exit(1)
    app = create_app(repo_path)
    script = Manager(app, with_default_commands=False)
    server = Server(use_debugger=True, use_reloader=False)
    server.description = 'runs the blohg local server.'
    script.add_command('run', server)
    return script
