# -*- coding: utf-8 -*-
"""
    blohg.tests.app
    ~~~~~~~~~~~~~~~

    Module with tests for blohg's flask application and the integration of the
    modules.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""


import codecs
import os
import unittest

from jinja2 import ChoiceLoader
from mercurial import commands, hg, ui
from shutil import rmtree
from tempfile import mkdtemp

from blohg import create_app
from blohg.utils import create_repo


class AppTestCase(unittest.TestCase):

    def setUp(self):
        self.repo_path = mkdtemp()
        self.ui = ui.ui()
        self.ui.setconfig('ui', 'quiet', True)
        create_repo(self.repo_path, self.ui)
        self.app = create_app(self.repo_path, self.ui)
        self.repo = hg.repository(self.ui, self.repo_path)

    def tearDown(self):
        try:
            rmtree(self.repo_path)
        except:
            pass

    def test_setup_app(self):
        self.assertTrue(hasattr(self.app, 'blohg'))
        self.assertTrue(isinstance(self.app.jinja_loader, ChoiceLoader),
                        'Invalid Jinja2 loader.')

    def test_reload_changectx_default(self):
        self.app.config['CHANGECTX'] = 'default'
        commands.add(self.ui, self.repo)
        commands.forget(self.ui, self.repo,
                        os.path.join(self.repo_path,
                                     self.app.config['CONTENT_DIR']))
        commands.commit(self.ui, self.repo, message='foo')
        client = self.app.test_client()
        rv = client.get('/')
        self.assertFalse('post/lorem-ipsum' in rv.data)
        self.assertFalse('post/example-post' in rv.data)
        commands.add(self.ui, self.repo)
        rv = client.get('/')
        self.assertFalse('post/lorem-ipsum' in rv.data)
        self.assertFalse('post/example-post' in rv.data)
        commands.commit(self.ui, self.repo, message='foo')
        rv = client.get('/')
        self.assertTrue('post/lorem-ipsum' in rv.data)
        self.assertTrue('post/example-post' in rv.data)
        with codecs.open(os.path.join(self.repo_path,
                                      self.app.config['CONTENT_DIR'],
                                      'about.rst'),
                         'a', encoding='utf-8') as fp:
            fp.write('\n\nTHIS IS A TEST!\n')
        rv = client.get('/about/')
        self.assertFalse('THIS IS A TEST!' in rv.data)
        commands.commit(self.ui, self.repo, message='foo')
        rv = client.get('/about/')
        self.assertTrue('THIS IS A TEST!' in rv.data)
        with codecs.open(os.path.join(self.repo_path,
                                      self.app.config['CONTENT_DIR'],
                                      'about.rst'),
                         'a', encoding='utf-8') as fp:
            fp.write('\n\nTHIS IS another TEST!\n')
        rv = client.get('/about/')
        self.assertTrue('THIS IS A TEST!' in rv.data)
        self.assertFalse('THIS IS another TEST!' in rv.data)
        commands.commit(self.ui, self.repo, message='foo')
        rv = client.get('/about/')
        self.assertTrue('THIS IS A TEST!' in rv.data)
        self.assertTrue('THIS IS another TEST!' in rv.data)

    def test_reload_changectx_working_dir(self):
        self.app.config['CHANGECTX'] = 'working_dir'
        client = self.app.test_client()
        rv = client.get('/')
        self.assertTrue('post/lorem-ipsum' in rv.data)
        self.assertTrue('post/example-post' in rv.data)
        commands.add(self.ui, self.repo)
        rv = client.get('/')
        self.assertTrue('post/lorem-ipsum' in rv.data)
        self.assertTrue('post/example-post' in rv.data)
        commands.commit(self.ui, self.repo, message='foo')
        rv = client.get('/')
        self.assertTrue('post/lorem-ipsum' in rv.data)
        self.assertTrue('post/example-post' in rv.data)
        with codecs.open(os.path.join(self.repo_path,
                                      self.app.config['CONTENT_DIR'],
                                      'about.rst'),
                         'a', encoding='utf-8') as fp:
            fp.write('\n\nTHIS IS A TEST!\n')
        rv = client.get('/about/')
        self.assertTrue('THIS IS A TEST!' in rv.data)
        commands.commit(self.ui, self.repo, message='foo')
        rv = client.get('/about/')
        self.assertTrue('THIS IS A TEST!' in rv.data)
        with codecs.open(os.path.join(self.repo_path,
                                      self.app.config['CONTENT_DIR'],
                                      'about.rst'),
                         'a', encoding='utf-8') as fp:
            fp.write('\n\nTHIS IS another TEST!\n')
        rv = client.get('/about/')
        self.assertTrue('THIS IS another TEST!' in rv.data)
        commands.commit(self.ui, self.repo, message='foo')
        rv = client.get('/about/')
        self.assertTrue('THIS IS another TEST!' in rv.data)
