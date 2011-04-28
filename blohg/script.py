# -*- coding: utf-8 -*-
"""
    blohg.script
    ~~~~~~~~~~~~
    
    Module with the CLI script related stuff.
    
    :copyright: (c) 2010-2011 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
import shutil
import sys

from flaskext.script import Command, Manager, Server
from mercurial import commands, ui, error
from pkg_resources import resource_filename, resource_listdir 

from blohg import create_app


class InitRepo(Command):
    """initialize a blohg repo, using the default template."""
    
    def handle(self, app):
        repo_path = app.config.get('REPO_PATH')
        template_path = resource_filename('blohg', 'repo_template')
        template_rootfiles = resource_listdir('blohg', 'repo_template')
        
        initialized = False
        for f in template_rootfiles + ['.hg']:
            if os.path.exists(os.path.join(repo_path, f)):
                initialized = True
                
        if initialized:
            print >> sys.stderr, 'repository already initialized: %s' % repo_path
            return
        
        if not os.path.exists(repo_path):
            os.makedirs(repo_path)
        
        for f in template_rootfiles:
            full_path = os.path.join(template_path, f)
            if os.path.isdir(full_path):
                shutil.copytree(full_path, os.path.join(repo_path, f))
            elif os.path.isfile(full_path):
                shutil.copy2(full_path, os.path.join(repo_path, f))
            else:
                print >> sys.stderr, 'unrecognized file: %s' % full_path
        
        try:
            commands.init(ui.ui(), repo_path)
        except error, err:
            print >> sys.stderr, 'an error was occurred: %s' % err


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
