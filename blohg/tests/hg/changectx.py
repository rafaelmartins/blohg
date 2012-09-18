# -*- coding: utf-8 -*-
"""
    blohg.tests.hg.changectx
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Module with tests for blohg integration with mercurial (change context).

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import codecs
import os
import unittest

from mercurial import commands, hg, ui
from shutil import rmtree
from tempfile import mkdtemp

from blohg.hg.changectx import ChangeCtxDefault, ChangeCtxWorkingDir


class ChangeCtxBaseTestCase(unittest.TestCase):

    def setUp(self):
        self.repo_path = mkdtemp()
        self.ui = ui.ui()
        self.ui.setconfig('ui', 'quiet', True)
        commands.init(self.ui, self.repo_path)

        # create files
        self.repo_files = ['a%i.rst' % i for i in range(5)]
        for i in self.repo_files:
            with codecs.open(os.path.join(self.repo_path, i), 'w',
                             encoding='utf-8') as fp:
                fp.write('dumb file %s\n' % i)

        self.repo = hg.repository(self.ui, self.repo_path)
        commands.commit(self.ui, self.repo, message='foo', addremove=True)

    def tearDown(self):
        try:
            rmtree(self.repo_path)
        except:
            pass

    @property
    def ctx_class(self):
        raise NotImplementedError

    def get_ctx(self):
        return self.ctx_class(self.repo, self.ui)


class ChangeCtxDefaultTestCase(ChangeCtxBaseTestCase):

    ctx_class = ChangeCtxDefault

    def test_files(self):

        new_file = 'a.rst'

        # add a file to repo
        with codecs.open(os.path.join(self.repo_path, new_file), 'w',
                         encoding='utf-8') as fp:
            fp.write('testing\n')

        # before commit files
        ctx = self.get_ctx()
        for f in self.repo_files:
            self.assertTrue(f in ctx.files, 'file not found in stable state: '
                            '%s' % f)
        self.assertFalse(new_file in ctx.files, 'stable state is '
                         'listing uncommited file.')

        commands.commit(self.ui, self.repo, message='foo', addremove=True)

        # after commit files
        ctx = self.get_ctx()
        for f in self.repo_files + [new_file]:
            self.assertTrue(f in ctx.files, 'file not found in stable '
                            'state: %s' % f)

    def test_needs_reload(self):
        ctx = self.get_ctx()
        self.assertFalse(ctx.needs_reload())

        # add a file to repo
        with codecs.open(os.path.join(self.repo_path, 'a.rst'), 'w',
                         encoding='utf-8') as fp:
            fp.write('testing\n')

        # should still be false
        self.assertFalse(ctx.needs_reload())

        commands.commit(self.ui, self.repo, message='foo', addremove=True)

        # should need a reload now, after the commit
        self.assertTrue(ctx.needs_reload())

        # reload
        ctx = self.get_ctx()

        # shouldn't need a reload again
        self.assertFalse(ctx.needs_reload())


class ChangeCtxWorkingDirTestCase(ChangeCtxBaseTestCase):

    ctx_class = ChangeCtxWorkingDir

    def test_files(self):

        new_file = 'a.rst'

        # add a file to repo
        with codecs.open(os.path.join(self.repo_path, new_file), 'w',
                         encoding='utf-8') as fp:
            fp.write('testing\n')

        # before commit files
        ctx = self.get_ctx()
        for f in self.repo_files + [new_file]:
            self.assertTrue(f in ctx.files, 'file not found in variable '
                            'state: %s' % f)
        self.assertTrue(new_file in ctx.files, 'variable state is not '
                        'listing uncommited file.')

        commands.commit(self.ui, self.repo, message='foo', addremove=True)

        # after commit files
        ctx = self.get_ctx()
        for f in self.repo_files + [new_file]:
            self.assertTrue(f in ctx.files, 'file not found in variable'
                            'state: %s' % f)

    def test_needs_reload(self):
        ctx = self.get_ctx()
        self.assertTrue(ctx.needs_reload())

        # add a file to repo
        with codecs.open(os.path.join(self.repo.path, 'a.rst'), 'w',
                         encoding='utf-8') as fp:
            fp.write('testing\n')

        # should always be true
        self.assertTrue(ctx.needs_reload())

        commands.commit(self.ui, self.repo, message='foo', addremove=True)

        # should need a reload now, after the commit
        self.assertTrue(ctx.needs_reload())

        # reload
        ctx = self.get_ctx()

        # should still need a reload, right after the reload
        self.assertTrue(ctx.needs_reload())