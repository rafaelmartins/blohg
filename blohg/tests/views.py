# -*- coding: utf-8 -*-
"""
    blohg.tests.views
    ~~~~~~~~~~~~~~~~~

    Module with tests for blohg views.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
import unittest
from hashlib import md5
from mercurial import commands, hg, ui
from shutil import rmtree
from tempfile import mkdtemp

from blohg import create_app
from blohg.vcs_backends.hg import HgRepository, REVISION_DEFAULT
from blohg.vcs_backends.hg.utils import u2hg


class ViewsTestCase(unittest.TestCase):

    def setUp(self):
        self.repo_path = mkdtemp()
        self.repo_pathb = u2hg(self.repo_path)
        self.ui = ui.ui()
        self.ui.setconfig(b'ui', b'quiet', True)
        HgRepository.create_repo(self.repo_path)
        self.repo = hg.repository(self.ui, self.repo_pathb)
        commands.commit(self.ui, self.repo, message=b'foo', user=b'foo',
                        addremove=True)
        self.app = create_app(repo_path=self.repo_path,
                              revision_id=REVISION_DEFAULT)

    def tearDown(self):
        try:
            rmtree(self.repo_path)
        except:
            pass

    def test_atom(self):
        c = self.app.test_client()
        rv = c.get('/atom/')
        self.assertTrue(b'<feed' in rv.data)
        for i in [b'/post/example-post/', b'/post/lorem-ipsum/']:
            self.assertTrue(i in rv.data, '%r not in atom feed' % i)
        rv = c.get('/atom/lorem-ipsum/')
        self.assertTrue(b'/post/lorem-ipsum/' in rv.data)
        rv = c.get('/atom/foo-bar/')
        self.assertEqual(rv.status_code, 404)

    def test_content(self):
        c = self.app.test_client()
        rv = c.get('/post/lorem-ipsum/')
        self.assertTrue(b'<html' in rv.data)
        self.assertTrue(b'/post/lorem-ipsum/' in rv.data)
        rv = c.get('/about/')
        self.assertTrue(b'<html' in rv.data)
        self.assertTrue(b'mercurial.png' in rv.data)
        self.assertTrue(b'/about/' in rv.data)
        rv = c.get('/post/foo-bar/')
        self.assertEqual(rv.status_code, 404)

    def test_home(self):
        c = self.app.test_client()
        rv = c.get('/')
        self.assertTrue(b'<html' in rv.data)
        for i in [b'/post/example-post/', b'/post/lorem-ipsum/']:
            self.assertTrue(i in rv.data, '%r not in home' % i)

    def test_post_list(self):
        c = self.app.test_client()
        rv = c.get('/post/')
        self.assertTrue(b'<html' in rv.data)
        for i in [b'/post/example-post/', b'/post/lorem-ipsum/']:
            self.assertTrue(i in rv.data, '%r not in post list' % i)

    def test_tag(self):
        c = self.app.test_client()
        rv = c.get('/tag/lorem-ipsum/')
        self.assertTrue(b'<html' in rv.data)
        self.assertTrue(b'/post/lorem-ipsum/' in rv.data)
        rv = c.get('/tag/foo-bar/')
        self.assertEqual(rv.status_code, 404)

    def test_source(self):
        c = self.app.test_client()
        rv = c.get('/source/post/lorem-ipsum/')
        self.assertTrue(b'=====' in rv.data)
        self.assertTrue(b'Lorem Ipsum' in rv.data)
        rv = c.get('/source/about/')
        self.assertTrue(b'=====' in rv.data)
        self.assertTrue(b'mercurial.png' in rv.data)
        rv = c.get('/source/post/foo-bar/')
        self.assertEqual(rv.status_code, 404)
        self.app.config['SHOW_RST_SOURCE'] = False
        rv = c.get('/source/post/lorem-ipsum/')
        self.assertEqual(rv.status_code, 404)

    def test_robots_txt(self):
        c = self.app.test_client()
        rv = c.get('/robots.txt')
        self.assertTrue(b'User-agent: *' in rv.data)

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
