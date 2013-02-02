# -*- coding: utf-8 -*-
"""
    blohg.vcs_backends.git
    ~~~~~~~~~~~~~~~~~~~~~~

    Package with all the classes and functions needed to deal with Git
    repositories. It uses pygit2 to access the repositories.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import codecs
import os
import shutil

from pygit2 import init_repository
from pkg_resources import resource_filename, resource_listdir
from blohg.vcs_backends.git.changectx import ChangeCtxDefault, \
     ChangeCtxWorkingDir
from blohg.vcs import Repository, REVISION_DEFAULT, REVISION_WORKING_DIR


class GitRepository(Repository):
    """Main entrypoint for the Git API layer. This class offers abstract
    access to everything needed by blohg from the low-level API.
    """

    identifier = 'git'
    name = 'Git'
    order = 10

    def get_changectx(self, revision=REVISION_DEFAULT):
        """Method that returns a change context for a given Revision state.

        blohg supports 2 revision states.

        - default: default revision, includes all the files that are tracked by
                   git, from the top of the 'master' branch.
        - working_dir: includes all the files in the git repository
                       directory, even the untracked ones, excluding the
                       .gitignore'd files.

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
        for f in template_rootfiles + ['.git']:
            if os.path.exists(os.path.join(repo_path, f)):
                initialized = True

        if initialized:
            raise RuntimeError('repository already initialized: %s' % \
                               repo_path)

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

        # create a .gitignore, to avoid people to acidentally push a build/ dir
        # with stuff built with 'blohg freeze'.
        with codecs.open(os.path.join(repo_path, '.gitignore'), 'w',
                         encoding='utf-8') as fp:
            fp.write('build' + os.linesep)

        try:
            init_repository(repo_path, False)
        except Exception, err:
            raise RuntimeError('an error was occurred: %s' % err)

    @staticmethod
    def supported(repo_path):
        if not os.path.isdir(repo_path):
            return False
        files = os.listdir(repo_path)
        if '.git' in files:
            return True
        for git_file in ['config', 'info', 'objects']:
            if git_file not in files:
                return False
        return True
