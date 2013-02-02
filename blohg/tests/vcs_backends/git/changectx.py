# -*- coding: utf-8 -*-
"""
    blohg.tests.vcs_backends.git.changectx
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Module with tests for blohg integration with git (change context).

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import codecs
import os
import unittest

from pygit2 import init_repository, Repository, Signature
from shutil import rmtree
from tempfile import mkdtemp
from time import sleep, time

from blohg.vcs_backends.git.changectx import ChangeCtxDefault, \
     ChangeCtxWorkingDir
from blohg.tests.vcs_backends.git.utils import git_commit


class ChangeCtxBaseTestCase(unittest.TestCase):

    def setUp(self):
        self.repo_path = mkdtemp()
        init_repository(self.repo_path, False)
        self.repo = Repository(self.repo_path)

        # create files and commit
        self.sign = Signature('foo', 'foo@example.com')
        self.repo_files = ['a%i.rst' % i for i in range(5)]
        for i in self.repo_files:
            with codecs.open(os.path.join(self.repo_path, i), 'w',
                             encoding='utf-8') as fp:
                fp.write('dumb file %s\n' % i)
        self.tree = self.repo.TreeBuilder()
        self.old_commit = git_commit(self.repo, self.tree, self.repo_files)

    def tearDown(self):
        try:
            rmtree(self.repo_path)
        except:
            pass

    @property
    def ctx_class(self):
        raise NotImplementedError

    def get_ctx(self):
        return self.ctx_class(self.repo_path)


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

        git_commit(self.repo, self.tree, [new_file], [self.old_commit])

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

        git_commit(self.repo, self.tree, ['a.rst'], [self.old_commit])

        # should need a reload now, after the commit
        self.assertTrue(ctx.needs_reload())

        # reload
        ctx = self.get_ctx()

        # shouldn't need a reload again
        self.assertFalse(ctx.needs_reload())

    def test_filectx_needs_reload(self):

        # add a file to repo
        with codecs.open(os.path.join(self.repo_path, 'a.rst'), 'w',
                         encoding='utf-8') as fp:
            fp.write('testing\n')

        self.old_commit = git_commit(self.repo, self.tree, ['a.rst'],
                                     [self.old_commit])

        ctx = self.get_ctx()
        filectx = ctx.get_filectx('a.rst')

        self.assertFalse(ctx.filectx_needs_reload(filectx))

        with codecs.open(os.path.join(self.repo_path, 'a.rst'), 'a',
                         encoding='utf-8') as fp:
            fp.write('lol\n')

        # should still be false
        self.assertFalse(ctx.filectx_needs_reload(filectx))

        git_commit(self.repo, self.tree, ['a.rst'], [self.old_commit])

        # should need a reload now, after the commit
        self.assertTrue(ctx.filectx_needs_reload(filectx))

        # reload
        ctx = self.get_ctx()
        filectx = ctx.get_filectx('a.rst')

        # shouldn't need a reload again
        self.assertFalse(ctx.filectx_needs_reload(filectx))

    def test_published(self):
        ctx = self.get_ctx()
        date = int(time() + 1)
        self.assertFalse(ctx.published(date, time()))
        sleep(1)
        self.assertTrue(ctx.published(date, time()))


class ChangeCtxWorkingDirTestCase(ChangeCtxBaseTestCase):

    ctx_class = ChangeCtxWorkingDir

    def test_files(self):

        new_file = 'a.rst'

        # add a file to repo
        with codecs.open(os.path.join(self.repo_path, new_file), 'w',
                         encoding='utf-8') as fp:
            fp.write('testing\n')
        self.repo.index.add(new_file)
        self.repo.index.write()

        # before commit files
        ctx = self.get_ctx()
        for f in self.repo_files + [new_file]:
            self.assertTrue(f in ctx.files, 'file not found in variable '
                            'state: %s' % f)
        self.assertTrue(new_file in ctx.files, 'variable state is not '
                        'listing uncommited file.')

        git_commit(self.repo, self.tree, [new_file], [self.old_commit])

        # after commit files
        ctx = self.get_ctx()
        for f in self.repo_files + [new_file]:
            self.assertTrue(f in ctx.files, 'file not found in variable'
                            'state: %s' % f)

    def test_needs_reload(self):
        ctx = self.get_ctx()
        self.assertTrue(ctx.needs_reload())

        # add a file to repo
        with codecs.open(os.path.join(self.repo_path, 'a.rst'), 'w',
                         encoding='utf-8') as fp:
            fp.write('testing\n')

        # should always be true
        self.assertTrue(ctx.needs_reload())

        git_commit(self.repo, self.tree, ['a.rst'], [self.old_commit])

        # should need a reload now, after the commit
        self.assertTrue(ctx.needs_reload())

        # reload
        ctx = self.get_ctx()

        # should still need a reload, right after the reload
        self.assertTrue(ctx.needs_reload())

    def test_filectx_needs_reload(self):

        # add a file to repo
        with codecs.open(os.path.join(self.repo_path, 'a.rst'), 'w',
                         encoding='utf-8') as fp:
            fp.write('testing\n')
        self.repo.index.add('a.rst')
        self.repo.index.write()

        ctx = self.get_ctx()
        filectx = ctx.get_filectx('a.rst')

        self.assertTrue(ctx.filectx_needs_reload(filectx))

        with codecs.open(os.path.join(self.repo_path, 'a.rst'), 'w',
                         encoding='utf-8') as fp:
            fp.write('testing\n')

        # should always be true
        self.assertTrue(ctx.filectx_needs_reload(filectx))

        git_commit(self.repo, self.tree, ['a.rst'], [self.old_commit])

        # should need a reload now, after the commit
        self.assertTrue(ctx.filectx_needs_reload(filectx))

        # reload
        ctx = self.get_ctx()
        filectx = ctx.get_filectx('a.rst')

        # should still need a reload, right after the reload
        self.assertTrue(ctx.filectx_needs_reload(filectx))

    def test_published(self):
        ctx = self.get_ctx()
        date = int(time() + 1)
        self.assertTrue(ctx.published(date, time()))
        sleep(1)
        self.assertTrue(ctx.published(date, time()))
