# -*- coding: utf-8 -*-
"""
    blohg.tests.utils
    ~~~~~~~~~~~~~~~~~

    Module with utilities for blohg tests.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
import unittest
from mercurial import hg, ui, commands
from shutil import rmtree
from tempfile import mkdtemp

from blohg import create_app
from blohg.utils import create_repo


def walk(p):
    def _walk(entries, path):
        for entry in os.listdir(path):
            full_entry = os.path.join(path, entry)
            if os.path.isdir(full_entry):
                _walk(entries, full_entry)
            else:
                entries.append(full_entry)
    e = []
    _walk(e, p)
    return e


class TestCaseWithNewRepo(unittest.TestCase):

    def setUp(self):
        self.repo_path = mkdtemp()
        self.ui = ui.ui()
        self.ui.setconfig('ui', 'quiet', True)
        self.ui.setconfig('ui', 'username', 'foo <foo@bar.com>')
        self.app = create_app(self.repo_path, hgui=self.ui)
        create_repo(self.app)
        self.repo = hg.repository(self.ui, self.repo_path)
        commands.add(self.ui, self.repo)
        self.app.hg.reload()

    def tearDown(self):
        try:
            rmtree(self.repo_path)
        except:
            pass

    def add(self, *pats, **opts):
        return commands.add(self.ui, self.repo, *pats, **opts)

    def commit(self, *pats, **opts):
        return commands.commit(self.ui, self.repo, *pats, **opts)
