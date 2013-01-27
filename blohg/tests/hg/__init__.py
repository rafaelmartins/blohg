# -*- coding: utf-8 -*-
"""
    blohg.tests.hg
    ~~~~~~~~~~~~~~

    Package with tests for blohg integration with mercurial.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import codecs
import os
import unittest
from mercurial import commands, hg, ui
from shutil import rmtree
from tempfile import mkdtemp

from blohg import REVISION_DEFAULT, REVISION_WORKING_DIR
from blohg.hg import HgRepository
from blohg.hg.changectx import ChangeCtxDefault, ChangeCtxWorkingDir


class HgRepositoryTestCase(unittest.TestCase):

    def setUp(self):
        self.repo_path = mkdtemp()
        self.ui = ui.ui()
        self.ui.setconfig('ui', 'quiet', True)
        commands.init(self.ui, self.repo_path)
        self.repo = hg.repository(self.ui, self.repo_path)

    def tearDown(self):
        try:
            rmtree(self.repo_path)
        except:
            pass

    def test_create_repo(self):
        repo_path = mkdtemp()
        try:
            HgRepository.create_repo(repo_path)
            for f in [os.path.join('content', 'attachments', 'mercurial.png'),
                      os.path.join('content', 'post', 'example-post.rst'),
                      os.path.join('content', 'post', 'lorem-ipsum.rst'),
                      os.path.join('content', 'about.rst'),
                      os.path.join('static', 'screen.css'),
                      os.path.join('templates', 'base.html'),
                      os.path.join('templates', 'posts.html'),
                      os.path.join('templates', 'post_list.html'),
                      'config.yaml', '.hgignore', '.hg']:
                self.assertTrue(os.path.exists(os.path.join(repo_path, f)),
                                'Not found: %s' % f)
        finally:
            rmtree(repo_path)

    def test_get_changectx_rev_default(self):
        hg_repo = HgRepository(self.repo_path)
        with codecs.open(os.path.join(self.repo_path, 'foo.rst'), 'w',
                         encoding='utf-8') as fp:
            fp.write('foo')
        commands.commit(self.ui, self.repo, message='foo', user='foo',
                        addremove=True)
        self.assertTrue(isinstance(hg_repo.get_changectx(REVISION_DEFAULT),
                                   ChangeCtxDefault),
                        'changectx object is not an instance of '
                        'ChangeCtxDefault')

    def test_get_changectx_rev_working_dir(self):
        hg_repo = HgRepository(self.repo_path)
        self.assertTrue(isinstance(hg_repo.get_changectx(REVISION_WORKING_DIR),
                                   ChangeCtxWorkingDir),
                        'changectx object is not an instance of '
                        'ChangeCtxWorkingDir')
