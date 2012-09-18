# -*- coding: utf-8 -*-
"""
    blohg.tests.utils
    ~~~~~~~~~~~~~~~~~

    Module with tests for blohg utilities.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
import unittest
from tempfile import mkdtemp
from shutil import rmtree

from blohg.utils import create_repo, parse_date


class UtilsTestCase(unittest.TestCase):

    def test_create_repo(self):
        repo_path = mkdtemp()
        try:
            create_repo(repo_path)
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

    def test_parse_date(self):
        # 1234567890 == 2009-02-13 23:31:30
        from_ts = parse_date('1234567890')
        from_str = parse_date('2009-02-13 23:31:30')
        self.assertTrue(isinstance(from_ts, int), 'parsed ts is not an int')
        self.assertTrue(isinstance(from_str, int), 'parsed str is not an int')
        self.assertEqual(from_ts, from_str)
