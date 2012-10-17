# -*- coding: utf-8 -*-
"""
    blohg.tests.templating
    ~~~~~~~~~~~~~~~~~~~~~~

    Module with tests for blohg integration with jinja2.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import codecs
import os
import unittest
from jinja2.exceptions import TemplateNotFound
from mercurial import commands, ui, hg
from shutil import rmtree
from tempfile import mkdtemp

from blohg import create_app
from blohg.utils import create_repo


class BlohgLoaderTestCase(unittest.TestCase):

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

    def test_up2date_changectx_default(self):
        self.app.config['CHANGECTX'] = 'default'
        with self.app.test_request_context():
            self.app.preprocess_request()
            self.assertRaises(TemplateNotFound,
                              self.app.jinja_loader.get_source,
                              self.app.jinja_env, 'test.html')
        new_file = os.path.join(self.repo_path,
                                self.app.config['TEMPLATES_DIR'], 'test.html')
        with codecs.open(new_file, 'w', encoding='utf-8') as fp:
            fp.write('foo')
        with self.app.test_request_context():
            self.app.preprocess_request()
            self.assertRaises(TemplateNotFound,
                              self.app.jinja_loader.get_source,
                              self.app.jinja_env, 'test.html')
        commands.commit(self.ui, self.repo, message='foo', user='foo',
                        addremove=True)
        with self.app.test_request_context():
            self.app.preprocess_request()
            contents, filename, up2date = self.app.jinja_loader.get_source(
                self.app.jinja_env, 'test.html')
            self.assertEqual('foo', contents)
            self.assertEqual(filename,
                              os.path.join(self.app.config['TEMPLATES_DIR'],
                                           'test.html'))
            self.assertTrue(up2date())
            with codecs.open(new_file, 'a', encoding='utf-8') as fp:
                fp.write('bar')
            self.assertTrue(up2date())
            commands.commit(self.ui, self.repo, message='foo', user='foo',
                            addremove=True)
            self.assertFalse(up2date())
            contents, filename, up2date = self.app.jinja_loader.get_source(
                self.app.jinja_env, 'test.html')
            self.assertEqual('foobar', contents)
            self.assertEqual(filename,
                              os.path.join(self.app.config['TEMPLATES_DIR'],
                                           'test.html'))
            self.assertTrue(up2date())

    def test_up2date_changectx_working_dir(self):
        self.app.config['CHANGECTX'] = 'working_dir'
        with self.app.test_request_context():
            self.app.preprocess_request()
            self.assertRaises(TemplateNotFound,
                              self.app.jinja_loader.get_source,
                              self.app.jinja_env, 'test.html')
        new_file = os.path.join(self.repo_path,
                                self.app.config['TEMPLATES_DIR'], 'test.html')
        with codecs.open(new_file, 'w', encoding='utf-8') as fp:
            fp.write('foo')
        with self.app.test_request_context():
            self.app.preprocess_request()
            contents, filename, up2date = self.app.jinja_loader.get_source(
                self.app.jinja_env, 'test.html')
            self.assertEqual('foo', contents)
            self.assertEqual(filename,
                              os.path.join(self.app.config['TEMPLATES_DIR'],
                                           'test.html'))
            self.assertFalse(up2date())
            commands.commit(self.ui, self.repo, message='foo', user='foo',
                            addremove=True)
            contents, filename, up2date = self.app.jinja_loader.get_source(
                self.app.jinja_env, 'test.html')
            self.assertEqual('foo', contents)
            self.assertFalse(up2date())

    def test_list_templates(self):
        self.app.config['CHANGECTX'] = 'working_dir'
        default_templates_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), '..', 'templates')
        templates_dir = os.path.join(self.repo_path,
                                     self.app.config['TEMPLATES_DIR'])
        real_files = os.listdir(default_templates_dir) + \
            os.listdir(templates_dir)
        with self.app.test_request_context():
            self.app.preprocess_request()
            self.assertEqual(sorted(real_files),
                              sorted(self.app.jinja_loader.list_templates()))
