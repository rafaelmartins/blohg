# -*- coding: utf-8 -*-
"""
    blohg.tests.views
    ~~~~~~~~~~~~~~~~~

    Module with tests for blohg views.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
import unittest
from hashlib import md5
from mercurial import commands, hg, ui
from shutil import rmtree
from tempfile import mkdtemp

from blohg import create_app
from blohg.hg import REVISION_DEFAULT
from blohg.utils import create_repo


class ViewsTestCase(unittest.TestCase):

    def setUp(self):
        self.repo_path = mkdtemp()
        self.ui = ui.ui()
        self.ui.setconfig('ui', 'quiet', True)
        create_repo(self.repo_path, self.ui)
        self.repo = hg.repository(self.ui, self.repo_path)
        commands.commit(self.ui, self.repo, message='foo', user='foo',
                        addremove=True)
        self.app = create_app(self.repo_path, self.ui, REVISION_DEFAULT)

    def tearDown(self):
        try:
            rmtree(self.repo_path)
        except:
            pass

    def test_atom(self):
        c = self.app.test_client()
        rv = c.get('/atom/')
        self.assertTrue('<feed' in rv.data)
        for i in ['/post/example-post/', '/post/lorem-ipsum/']:
            self.assertTrue(i in rv.data, '%r not in atom feed' % i)
        rv = c.get('/atom/lorem-ipsum/')
        self.assertTrue('/post/lorem-ipsum/' in rv.data)
        rv = c.get('/atom/foo-bar/')
        self.assertEqual(rv.status_code, 404)

    def test_content(self):
        c = self.app.test_client()
        rv = c.get('/post/lorem-ipsum/')
        self.assertTrue('<html' in rv.data)
        self.assertTrue('/post/lorem-ipsum/' in rv.data)
        rv = c.get('/about/')
        self.assertTrue('<html' in rv.data)
        self.assertTrue('mercurial.png' in rv.data)
        self.assertTrue('/about/' in rv.data)
        rv = c.get('/post/foo-bar/')
        self.assertEqual(rv.status_code, 404)

    def test_home(self):
        c = self.app.test_client()
        rv = c.get('/')
        self.assertTrue('<html' in rv.data)
        for i in ['/post/example-post/', '/post/lorem-ipsum/']:
            self.assertTrue(i in rv.data, '%r not in home' % i)

    def test_post_list(self):
        c = self.app.test_client()
        rv = c.get('/post/')
        self.assertTrue('<html' in rv.data)
        for i in ['/post/example-post/', '/post/lorem-ipsum/']:
            self.assertTrue(i in rv.data, '%r not in post list' % i)

    def test_tag(self):
        c = self.app.test_client()
        rv = c.get('/tag/lorem-ipsum/')
        self.assertTrue('<html' in rv.data)
        self.assertTrue('/post/lorem-ipsum/' in rv.data)
        rv = c.get('/tag/foo-bar/')
        self.assertEqual(rv.status_code, 404)

    def test_source(self):
        c = self.app.test_client()
        rv = c.get('/source/post/lorem-ipsum/')
        self.assertTrue('=====' in rv.data)
        self.assertTrue('Lorem Ipsum' in rv.data)
        rv = c.get('/source/about/')
        self.assertTrue('=====' in rv.data)
        self.assertTrue('mercurial.png' in rv.data)
        rv = c.get('/source/post/foo-bar/')
        self.assertEqual(rv.status_code, 404)
        self.app.config['SHOW_RST_SOURCE'] = False
        rv = c.get('/source/post/lorem-ipsum/')
        self.assertEqual(rv.status_code, 404)

    def test_robots_txt(self):
        c = self.app.test_client()
        rv = c.get('/robots.txt')
        self.assertTrue('User-agent: *' in rv.data)

    def test_attachments(self):
        c = self.app.test_client()
        rv = c.get('/attachments/mercurial.png')
        h1 = md5(rv.data).hexdigest()
        file_path = os.path.join(self.repo_path,
                                 self.app.config['ATTACHMENT_DIR'],
                                 'mercurial.png')
        with open(file_path, 'rb') as fp:
            h2 = md5(fp.read()).hexdigest()
        self.assertEqual(h1, h2)
