# -*- coding: utf-8 -*-
"""
    blohg.tests.hgapi.repo
    ~~~~~~~~~~~~~~~~~~~~~~

    Module with tests for blohg low-level integration with mercurial.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import codecs
import os
import unittest
from mercurial import commands, ui
from shutil import rmtree
from tempfile import mkdtemp

from blohg.hgapi.repo import Repository, RepoStateStable, RepoStateVariable, \
     STATE_STABLE, STATE_VARIABLE


class RepoStateBaseTestCase(unittest.TestCase):

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

        self.repo = Repository(self.repo_path, self.ui)
        self.repo.commit(message='foo', addremove=True)

    def tearDown(self):
        try:
            rmtree(self.repo_path)
        except:
            pass


class RepoStateStableTestCase(RepoStateBaseTestCase):

    def test_files(self):

        new_file = 'a.rst'

        # add a file to repo
        with codecs.open(os.path.join(self.repo.path, new_file), 'w',
                         encoding='utf-8') as fp:
            fp.write('testing\n')

        # before commit files
        state = self.repo.get_repostate(STATE_STABLE)
        for f in self.repo_files:
            self.assertTrue(f in state.files, 'file not found in stable'
                            'state: %s' % f)
        self.assertFalse(new_file in state.files, 'stable state is '
                         'listing uncommited file.')

        self.repo.commit(message='foo', addremove=True)

        # after commit files
        state = self.repo.get_repostate(STATE_STABLE)
        for f in self.repo_files + [new_file]:
            self.assertTrue(f in state.files, 'file not found in stable'
                            'state: %s' % f)

    def test_needs_reload(self):
        state = self.repo.get_repostate(STATE_STABLE)
        self.assertFalse(state.needs_reload())

        # add a file to repo
        with codecs.open(os.path.join(self.repo.path, 'a.rst'), 'w',
                         encoding='utf-8') as fp:
            fp.write('testing\n')

        # should still be false
        self.assertFalse(state.needs_reload())

        self.repo.commit(message='foo', addremove=True)

        # should need a reload now, after the commit
        self.assertTrue(state.needs_reload())

        # reload
        state = self.repo.get_repostate(STATE_STABLE)

        # shouldn't need a reload again
        self.assertFalse(state.needs_reload())


class RepoStateVariableTestCase(RepoStateBaseTestCase):

    def test_files(self):

        new_file = 'a.rst'

        # add a file to repo
        with codecs.open(os.path.join(self.repo.path, new_file), 'w',
                         encoding='utf-8') as fp:
            fp.write('testing\n')

        # before commit files
        state = self.repo.get_repostate(STATE_VARIABLE)
        for f in self.repo_files + [new_file]:
            self.assertTrue(f in state.files, 'file not found in variable'
                            'state: %s' % f)
        self.assertTrue(new_file in state.files, 'variable state is not '
                        'listing uncommited file.')

        self.repo.commit(message='foo', addremove=True)

        # after commit files
        state = self.repo.get_repostate(STATE_VARIABLE)
        for f in self.repo_files + [new_file]:
            self.assertTrue(f in state.files, 'file not found in variable'
                            'state: %s' % f)

    def test_needs_reload(self):
        state = self.repo.get_repostate(STATE_VARIABLE)
        self.assertTrue(state.needs_reload())

        # add a file to repo
        with codecs.open(os.path.join(self.repo.path, 'a.rst'), 'w',
                         encoding='utf-8') as fp:
            fp.write('testing\n')

        # should always be true
        self.assertTrue(state.needs_reload())

        self.repo.commit(message='foo', addremove=True)

        # should need a reload now, after the commit
        self.assertTrue(state.needs_reload())

        # reload
        state = self.repo.get_repostate(STATE_VARIABLE)

        # should still need a reload, right after the reload
        self.assertTrue(state.needs_reload())


class RepositoryTestCase(RepoStateBaseTestCase):

    def test_state_stable(self):
        self.assertTrue(isinstance(self.repo.get_repostate(STATE_STABLE),
                                   RepoStateStable), 'stable state object '
                        'is not an instance of RepoStateStable')

    def test_state_variable(self):
        self.assertTrue(isinstance(self.repo.get_repostate(STATE_VARIABLE),
                                   RepoStateVariable), 'variable state object '
                        'is not an instance of RepoStateVariable')
