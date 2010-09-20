# -*- coding: utf-8 -*-

import os, sys

from flaskext.script import Server, Manager
from blohg import create_app

def create_script(config_file):
    if not os.path.exists('.hg') or not os.path.exists(config_file):
        print >> sys.stderr, 'error: invalid Mercurial repository!'
        sys.exit(1)
    script = Manager(create_app(config_file), with_default_commands=False)
    server = Server(use_debugger=False, use_reloader=False)
    server.description = 'runs the blohg local server.'
    script.add_command('run', server)
    return script
