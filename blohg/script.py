# -*- coding: utf-8 -*-
"""
    blohg.script
    ~~~~~~~~~~~~
    
    Module with the CLI script related stuff.
    
    :copyright: (c) 2010-2011 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
from flaskext.script import Server, Manager

from blohg import create_app


def create_script():
    """Script object factory
    
    :param repo_path: the path to the mercurial repository.
    :return: the script object (Flask-Script' Manager instance).
    """
    
    script = Manager(create_app, with_default_commands=True)
    script.add_option('--repo-path', dest='repo_path', default=os.getcwd(),
        required=False)
    return script
