# -*- coding: utf-8 -*-
"""
    blohg.tests.git
    ~~~~~~~~~~~~~~~

    Package with tests for blohg integration with git.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import codecs
import os
import unittest
from pygit2 import init_repository, Repository, Signature
from shutil import rmtree
from tempfile import mkdtemp

from blohg.git import GitRepository, REVISION_DEFAULT, REVISION_WORKING_DIR
from blohg.git.changectx import ChangeCtxDefault, ChangeCtxWorkingDir


class GitRepositoryTestCase(unittest.TestCase):

    def setUp(self):
        self.repo_path = mkdtemp()
        init_repository(self.repo_path, False)
        self.repo = Repository(self.repo_path)

    def tearDown(self):
        try:
            rmtree(self.repo_path)
        except:
            pass

    def test_create_repo(self):
        repo_path = mkdtemp()
        try:
            GitRepository.create_repo(repo_path)
            for f in [os.path.join('content', 'attachments', 'mercurial.png'),
                      os.path.join('content', 'post', 'example-post.rst'),
                      os.path.join('content', 'post', 'lorem-ipsum.rst'),
                      os.path.join('content', 'about.rst'),
                      os.path.join('static', 'screen.css'),
                      os.path.join('templates', 'base.html'),
                      os.path.join('templates', 'posts.html'),
                      os.path.join('templates', 'post_list.html'),
                      'config.yaml', '.gitignore', '.git']:
                self.assertTrue(os.path.exists(os.path.join(repo_path, f)),
                                'Not found: %s' % f)
        finally:
            rmtree(repo_path)

    def test_get_changectx_rev_default(self):
        git_repo = GitRepository(self.repo_path)
        with codecs.open(os.path.join(self.repo_path, 'foo.rst'), 'w',
                         encoding='utf-8') as fp:
            fp.write('foo')
        sign = Signature('foo', 'foo@example.com')
        tree = self.repo.TreeBuilder().write()
        self.repo.index.add('foo.rst')
        self.repo.create_commit('refs/heads/master', sign, sign, 'foo', tree,
                                [])
        self.assertTrue(isinstance(git_repo.get_changectx(REVISION_DEFAULT),
                                   ChangeCtxDefault),
                        'changectx object is not an instance of '
                        'ChangeCtxDefault')

    def test_get_changectx_rev_working_dir(self):
        git_repo = GitRepository(self.repo_path)
        with codecs.open(os.path.join(self.repo_path, 'foo.rst'), 'w',
                         encoding='utf-8') as fp:
            fp.write('foo')
        sign = Signature('foo', 'foo@example.com')
        tree = self.repo.TreeBuilder().write()
        self.repo.index.add('foo.rst')
        self.repo.create_commit('refs/heads/master', sign, sign, 'foo', tree,
                                [])
        self.assertTrue(
            isinstance(git_repo.get_changectx(REVISION_WORKING_DIR),
                       ChangeCtxWorkingDir),
            'changectx object is not an instance of ChangeCtxWorkingDir')
