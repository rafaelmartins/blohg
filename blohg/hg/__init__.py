# -*- coding: utf-8 -*-
"""
    blohg.hg
    ~~~~~~~~

    Package with all the classes and functions needed to deal with Mercurial's
    low-level API.

    .. warning::

        Mercurial API isn't stable, according with their own wiki
        (http://mercurial.selenic.com/wiki/MercurialApi). This package needs to
        be well tested against new releases of Mercurial.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import codecs
import os
import shutil

from mercurial import commands, error, ui as _ui
from pkg_resources import resource_filename, resource_listdir
from blohg.hg.changectx import ChangeCtxDefault, ChangeCtxWorkingDir

REVISION_WORKING_DIR = 1
REVISION_DEFAULT = 2


class HgRepository(object):
    """Main entrypoint for the Mercurial API layer. This class offers abstract
    access to everything needed by blohg from the low-level API.
    """

    def __init__(self, path):
        self.path = path

    def get_changectx(self, revision=REVISION_DEFAULT):
        """Method that returns a change context for a given Revision state.

        blohg supports 2 revision states.

        - default: default revision, includes all the files that are tracked by
                   mercurial, from the top of the 'default' branch.
        - working_dir: includes all the files in the mercurial repository
                       directory, even the untracked ones, excluding the
                       .hgignore'd files.

        Change contexts are represented by instances of classes
        (:class:`ChangeCtxDefault` and :class:`ChangeCtxWorkingDir`), that
        provides access to everything related to the repository, filtered by
        the revision state, like: list of files, content of files, etc. The
        repository state object will be used later by the parsers to generate
        content suitable for publishing.
        """
        if revision == REVISION_DEFAULT:
            return ChangeCtxDefault(self.path)
        elif revision == REVISION_WORKING_DIR:
            return ChangeCtxWorkingDir(self.path)
        raise RuntimeError('Invalid repository revision: %r' % revision)

    @staticmethod
    def create_repo(repo_path):
        """Function to initialize a blohg repo, with the default template files
        inside.
        """

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

        ui = _ui.ui()
        ui.setconfig('ui', 'quiet', True)
        try:
            commands.init(ui, repo_path)
        except error, err:
            raise RuntimeError('an error was occurred: %s' % err)
