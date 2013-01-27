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
from shutil import rmtree
from tempfile import mkdtemp

from blohg.git import GitRepository


class GitRepositoryTestCase(unittest.TestCase):

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