# -*- coding: utf-8 -*-
"""
    blohg.tests.hgapi
    ~~~~~~~~~~~~~~~~~

    Module with tests for blohg integration with mercurial.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import codecs
import os
import posixpath
import unittest
from jinja2.loaders import ChoiceLoader
from mercurial import commands, hg, ui
from shutil import rmtree
from tempfile import mkdtemp

from blohg import create_app
from blohg.utils import create_repo


class HgApiTestCase(unittest.TestCase):

    def setUp(self):
        self.repo_path = mkdtemp()
        self.ui = ui.ui()
        self.ui.setconfig('ui', 'quiet', True)
        self.ui.setconfig('ui', 'username', 'foo <foo@bar.com>')
        create_repo(self.repo_path, self.ui)
        self.app = create_app(self.repo_path, self.ui)
        self.app.hg.repo.commit(message='foo', addremove=True)

    def tearDown(self):
        try:
            rmtree(self.repo_path)
        except:
            pass

    def test_setup_mercurial(self):
        self.assertTrue(hasattr(self.app, 'hg'), 'mercurial not setup.')
        self.assertTrue(isinstance(self.app.jinja_loader, ChoiceLoader),
                        'Invalid Jinja2 loader.')

    def test_reload(self):
        self.app.hg.reload()
