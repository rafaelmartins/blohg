# -*- coding: utf-8 -*-
"""
    blohg.script
    ~~~~~~~~~~~~

    Module with the CLI script related stuff.

    :copyright: (c) 2010-2011 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
import sys
from flaskext.script import Command, Manager, Server

from blohg import create_app
from blohg.utils import create_repo


class InitRepo(Command):
    """initialize a blohg repo, using the default template."""

    def handle(self, app):
        try:
            create_repo(app)
        except RuntimeError, err:
            print >> sys.stderr, str(err)


def create_script():
    """Script object factory

    :param repo_path: the path to the mercurial repository.
    :return: the script object (Flask-Script' Manager instance).
    """

    script = Manager(create_app, with_default_commands=False)
    script.add_option('-r', '--repo-path', dest='repo_path', default=os.getcwd(),
        required=False)
    server = Server(use_debugger=True, use_reloader=True)
    server.description = 'runs the blohg local server.'
    script.add_command('runserver', server)
    script.add_command('initrepo', InitRepo())

    return script
