# -*- coding: utf-8 -*-
"""
    blohg.utils
    ~~~~~~~~~~~

    Module with general purpose utilities for blohg.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import codecs
import os
import shutil

from mercurial import commands, ui, error
from pkg_resources import resource_filename, resource_listdir


def create_repo(app):
    """Function to initialize a blohg repo, with the default template files
    inside.
    """

    repo_path = app.config.get('REPO_PATH')
    template_path = resource_filename('blohg', 'repo_template')
    template_rootfiles = resource_listdir('blohg', 'repo_template')

    initialized = False
    for f in template_rootfiles + ['.hg']:
        if os.path.exists(os.path.join(repo_path, f)):
            initialized = True

    if initialized:
        raise RuntimeError('repository already initialized: %s' % repo_path)

    if not os.path.exists(repo_path):
        os.makedirs(repo_path)

    for f in template_rootfiles:
        full_path = os.path.join(template_path, f)
        if os.path.isdir(full_path):
            shutil.copytree(full_path, os.path.join(repo_path, f))
        elif os.path.isfile(full_path):
            shutil.copy2(full_path, os.path.join(repo_path, f))
        else:
            raise RuntimeError('unrecognized file: %s' % full_path)

    # create a .hgignore, to avoid people to acidentally push a build/ dir
    # with stuff built with 'blohg freeze'. creating the file here because a
    # .hgignore file in the repo may cause some weird behavior that we are not
    # aware of.
    with codecs.open(os.path.join(repo_path, '.hgignore'), 'w',
                     encoding='utf-8') as fp:
        fp.write('^build/' + os.linesep)

    try:
        commands.init(ui.ui(), repo_path)
    except error, err:
        raise RuntimeError('an error was occurred: %s' % err)
