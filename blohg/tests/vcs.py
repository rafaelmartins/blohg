# -*- coding: utf-8 -*-
"""
    blohg.tests.vcs
    ~~~~~~~~~~~~~~~

    Module with tests for blohg VCS backends infrastructure.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import unittest
from pygit2 import init_repository
from tempfile import mkdtemp

from blohg.hg import HgRepository
from blohg.git import GitRepository
from blohg.vcs import load_repo

class LoadRepoTestCase(unittest.TestCase):

    def setUp(self):
        self.repo_path = mkdtemp()

    def tearDown(self):
        try:
            rmtree(self.repo_path)
        except:
            pass

    def test_load_hg_repository(self):
        HgRepository.create_repo(self.repo_path)
        repo = load_repo(self.repo_path)
        self.assertTrue(isinstance(repo, HgRepository))

    def test_load_git_repository(self):
        GitRepository.create_repo(self.repo_path)
        repo = load_repo(self.repo_path)
        self.assertTrue(isinstance(repo, GitRepository))

    def test_load_git_bare_repository(self):
        init_repository(self.repo_path, True)
        repo = load_repo(self.repo_path)
        self.assertTrue(isinstance(repo, GitRepository))
