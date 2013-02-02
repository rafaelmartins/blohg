# -*- coding: utf-8 -*-
"""
    blohg.tests.vcs_backends.hg.filectx
    ~~~~~~~~~~~~~~~~~~~~~~

    Module with tests for blohg integration with mercurial (file context).

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import codecs
import os
import time
import unittest
from mercurial import commands, hg, ui
from shutil import rmtree
from tempfile import mkdtemp

from blohg.vcs_backends.hg.filectx import FileCtx


class FileCtxTestCase(unittest.TestCase):

    def setUp(self):
        self.repo_path = mkdtemp()
        self.ui = ui.ui()
        self.ui.setconfig('ui', 'quiet', True)
        commands.init(self.ui, self.repo_path)
        self.file_name = 'foo.rst'
        self.file_path = os.path.join(self.repo_path, self.file_name)
        with codecs.open(self.file_path, 'w', encoding='utf-8') as fp:
            fp.write('test\n')
        self.repo = hg.repository(self.ui, self.repo_path)
        self.changectx = self.repo[None]
        commands.commit(self.ui, self.repo, message='foo',
                        user='foo <foo@bar.com>', addremove=True)

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
        self.assertEqual(ctx.author, 'foo <foo@bar.com>')

    def test_date_and_mdate(self):
        ctx = FileCtx(self.repo, self.changectx, self.file_name)
        time.sleep(1)
        self.assertTrue(ctx.date < time.time())
        self.assertTrue(ctx.mdate is None)
        old_date = ctx.date
        time.sleep(1)
        with codecs.open(self.file_path, 'a', encoding='utf-8') as fp:
            fp.write('foo\n')
        commands.commit(self.ui, self.repo, user='foo', message='foo2')
        ctx = FileCtx(self.repo, self.changectx, self.file_name)
        self.assertEqual(ctx.date, old_date)
        self.assertTrue(ctx.mdate > old_date)
