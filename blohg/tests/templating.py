# -*- coding: utf-8 -*-
"""
    blohg.tests.templating
    ~~~~~~~~~~~~~~~~~~~~~~

    Module with tests for blohg integration with jinja2.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
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
from blohg.vcs_backends.hg import HgRepository
from blohg.vcs import REVISION_DEFAULT, REVISION_WORKING_DIR


class BlohgLoaderTestCase(unittest.TestCase):

    def setUp(self):
        self.repo_path = mkdtemp()
        self.ui = ui.ui()
        self.ui.setconfig('ui', 'quiet', True)
        HgRepository.create_repo(self.repo_path)
        self.repo = hg.repository(self.ui, self.repo_path)

    def tearDown(self):
        try:
            rmtree(self.repo_path)
        except:
            pass

    def test_up2date_changectx_default(self):
        app = create_app(repo_path=self.repo_path, autoinit=False)
        new_file = os.path.join(self.repo_path, 'foo')
        with codecs.open(new_file, 'w', encoding='utf-8') as fp:
            fp.write('foo')
        commands.commit(self.ui, self.repo, message='foo', user='foo',
                        addremove=True)
        app.blohg.init_repo(REVISION_DEFAULT)
        with app.test_request_context():
            app.preprocess_request()
            self.assertRaises(TemplateNotFound, app.jinja_loader.get_source,
                              app.jinja_env, 'test.html')
        new_file = os.path.join(self.repo_path,
                                app.config['TEMPLATES_DIR'], 'test.html')
        with codecs.open(new_file, 'w', encoding='utf-8') as fp:
            fp.write('foo')
        with app.test_request_context():
            app.preprocess_request()
            self.assertRaises(TemplateNotFound, app.jinja_loader.get_source,
                              app.jinja_env, 'test.html')
        commands.commit(self.ui, self.repo, message='foo', user='foo',
                        addremove=True)
        with app.test_request_context():
            app.preprocess_request()
            contents, filename, up2date = app.jinja_loader.get_source(
                app.jinja_env, 'test.html')
            self.assertEqual('foo', contents)
            self.assertEqual(filename,
                             os.path.join(app.config['TEMPLATES_DIR'],
                                          'test.html'))
            app.preprocess_request()
            self.assertTrue(up2date())
            with codecs.open(new_file, 'a', encoding='utf-8') as fp:
                fp.write('bar')
            app.preprocess_request()
            self.assertTrue(up2date())
            commands.commit(self.ui, self.repo, message='foo', user='foo',
                            addremove=True)
            app.preprocess_request()
            self.assertFalse(up2date())
            contents, filename, up2date = app.jinja_loader.get_source(
                app.jinja_env, 'test.html')
            self.assertEqual('foobar', contents)
            self.assertEqual(filename,
                              os.path.join(app.config['TEMPLATES_DIR'],
                                           'test.html'))
            app.preprocess_request()
            self.assertTrue(up2date())

    def test_up2date_changectx_working_dir(self):
        app = create_app(repo_path=self.repo_path,
                         revision_id=REVISION_WORKING_DIR)
        with app.test_request_context():
            app.preprocess_request()
            self.assertRaises(TemplateNotFound, app.jinja_loader.get_source,
                              app.jinja_env, 'test.html')
        new_file = os.path.join(self.repo_path,
                                app.config['TEMPLATES_DIR'], 'test.html')
        with codecs.open(new_file, 'w', encoding='utf-8') as fp:
            fp.write('foo')
        with app.test_request_context():
            app.preprocess_request()
            contents, filename, up2date = app.jinja_loader.get_source(
                app.jinja_env, 'test.html')
            self.assertEqual('foo', contents)
            self.assertEqual(filename,
                              os.path.join(app.config['TEMPLATES_DIR'],
                                           'test.html'))
            app.preprocess_request()
            self.assertFalse(up2date())
            commands.commit(self.ui, self.repo, message='foo', user='foo',
                            addremove=True)
            contents, filename, up2date = app.jinja_loader.get_source(
                app.jinja_env, 'test.html')
            self.assertEqual('foo', contents)
            app.preprocess_request()
            self.assertFalse(up2date())

    def test_list_templates(self):
        app = create_app(repo_path=self.repo_path,
                         revision_id=REVISION_WORKING_DIR)
        default_templates_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), '..', 'templates')
        templates_dir = os.path.join(self.repo_path,
                                     app.config['TEMPLATES_DIR'])
        real_files = os.listdir(default_templates_dir) + \
            os.listdir(templates_dir)
        with app.test_request_context():
            app.preprocess_request()
            self.assertEqual(sorted(real_files),
                              sorted(app.jinja_loader.list_templates()))
