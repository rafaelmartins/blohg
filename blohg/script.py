# -*- coding: utf-8 -*-
"""
    blohg.script
    ~~~~~~~~~~~~
    
    Module with the CLI script related stuff.
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: BSD, see LICENSE for more details.
"""

import os, sys
from flaskext.script import Server, Manager

from blohg import create_app


def create_script(config_file):
    """Script object factory
    
    :param config_file: the configuration file path.
    :return: the script object (Flask-Themes' Manager instance).
    """
    
    if not os.path.exists('.hg') or not os.path.exists(config_file):
        print >> sys.stderr, 'error: invalid Mercurial repository!'
        sys.exit(1)
    app = create_app(config_file)
    app.debug = True
    script = Manager(app, with_default_commands=False)
    server = Server(use_debugger=False, use_reloader=False)
    server.description = 'runs the blohg local server.'
    script.add_command('run', server)
    return script
