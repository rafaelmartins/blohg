# -*- coding: utf-8 -*-
"""
    blohg.tests.git.filectx
    ~~~~~~~~~~~~~~~~~~~~~~~

    Module with tests for blohg integration with git (file context).

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import codecs
import os
import time
import unittest
from pygit2 import init_repository, Repository
from shutil import rmtree
from tempfile import mkdtemp

from blohg.git.filectx import FileCtx
from blohg.tests.git.utils import git_commit


class FileCtxTestCase(unittest.TestCase):

    def setUp(self):
        self.repo_path = mkdtemp()
        init_repository(self.repo_path, False)
        self.repo = Repository(self.repo_path)
        self.file_name = 'foo.rst'
        self.file_path = os.path.join(self.repo_path, self.file_name)
        with codecs.open(self.file_path, 'w', encoding='utf-8') as fp:
            fp.write('test\n')
        self.tree = self.repo.TreeBuilder()
        self.last_commit = git_commit(self.repo, self.tree, [self.file_name])
        self.changectx = self.repo.head

    def tearDown(self):
        try:
            rmtree(self.repo_path)
        except:
            pass

    def test_path(self):
        ctx = FileCtx(self.repo, self.changectx, self.file_name)
        self.assertEqual(ctx.path, 'foo.rst')

    def test_content(self):
        ctx = FileCtx(self.repo, self.changectx, self.file_name)
        self.assertEqual(ctx.content, 'test\n')

    def test_author(self):
        ctx = FileCtx(self.repo, self.changectx, self.file_name)
        self.assertEqual(ctx.author, 'foo <foo@example.com>')

    def test_date_and_mdate(self):
        ctx = FileCtx(self.repo, self.changectx, self.file_name)
        time.sleep(1)
        self.assertTrue(ctx.date < time.time())
        self.assertTrue(ctx.mdate is None)
        old_date = ctx.date
        time.sleep(1)
        with codecs.open(self.file_path, 'a', encoding='utf-8') as fp:
            fp.write('foo\n')
        git_commit(self.repo, self.tree, [self.file_name], [self.last_commit])
        ctx = FileCtx(self.repo, self.changectx, self.file_name)
        self.assertEqual(ctx.date, old_date)
        self.assertTrue(ctx.mdate > old_date)
