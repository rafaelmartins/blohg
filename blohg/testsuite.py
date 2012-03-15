# -*- coding: utf-8 -*-
"""
    blohg.testsuite
    ~~~~~~~~~~~~~~~

    Module with a simple test suite for blohg.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import codecs
import os
import posixpath
import unittest
from jinja2.loaders import ChoiceLoader
from jinja2.exceptions import TemplateNotFound
from mercurial import hg, ui, commands
from shutil import rmtree
from tempfile import mkdtemp

from blohg import create_app
from blohg.utils import create_repo


def _walk(p):
    def walk(entries, path):
        for entry in os.listdir(path):
            full_entry = os.path.join(path, entry)
            if os.path.isdir(full_entry):
                walk(entries, full_entry)
            else:
                entries.append(full_entry)
    e = []
    walk(e, p)
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


class HgApiTestCase(TestCaseWithNewRepo):

    def test_repo_structure(self):
        for f in [posixpath.join('content', 'attachments', 'mercurial.png'),
                  posixpath.join('content', 'post', 'example-post.rst'),
                  posixpath.join('content', 'post', 'lorem-ipsum.rst'),
                  posixpath.join('content', 'about.rst'),
                  posixpath.join('static', 'screen.css'),
                  posixpath.join('templates', 'base.html'),
                  posixpath.join('templates', 'posts.html'),
                  posixpath.join('templates', 'post_list.html'),
                  'config.yaml', '.hgignore']:
            self.assertTrue(f in self.app.hg.revision.manifest(),
                            'File not found: %s' % f)

    def test_setup_mercurial(self):
        self.assertTrue(hasattr(self.app, 'hg'), 'mercurial not setup.')
        self.assertTrue(isinstance(self.app.jinja_loader, ChoiceLoader),
                        'Invalid Jinja2 loader.')

    def test_get_page(self):
        with self.app.test_request_context():
            data = self.app.hg.get('about')
            self.assertFalse(data is None, 'Page not found: about')
            self.assertTrue('About me' in data.title,
                            'Failed to parse the title')
            self.assertTrue('<img' in data.full_html,
                            'reStructuredText parser failed')
            self.assertEqual(data.path, 'content/about.rst', 'Invalid path')
            self.assertEqual(data.slug, 'about', 'Failed to parse the slug')
            self.assertEqual(data.author_name, 'foo',
                             'Failed to parse author name')
            self.assertEqual(data.author_email, 'foo@bar.com',
                             'Failed to parse author email')

            # TODO: test aliases

    def test_get_post(self):
        with self.app.test_request_context():
            data = self.app.hg.get('post/lorem-ipsum')
            self.assertFalse(data is None, 'Page not found: post/lorem-ipsum')
            self.assertTrue('lorem-ipsum' in data.tags,
                            'Failed to parse the tags')

    def test_reload(self):
        with self.app.test_request_context():
            data = self.app.hg.get('post/foo-bar')
            self.assertTrue(data is None,
                            'New post found before created! ' \
                            'Run to the hills :P')

        new_file = os.path.join(self.repo_path, 'content', 'post',
                                'foo-bar.rst')
        with codecs.open(new_file, 'w', encoding='utf-8') as fp:
            fp.write(os.linesep.join(['Foo', '---', '', 'Bar']))

        self.app.hg.reload()
        with self.app.test_request_context():
            data = self.app.hg.get('post/foo-bar')
            self.assertTrue(data is None, 'Reload failed. Uncommited stuff ' \
                            'was reloaded, with debug disabled')

        self.app.debug = True
        self.app.hg.reload()
        with self.app.test_request_context():
            data = self.app.hg.get('post/foo-bar')
            self.assertFalse(data is None, 'Reload failed. Uncommited stuff ' \
                             'wasn\'t reloaded, with debug enabled')

        self.app.debug = False
        self.commit(message='foo', addremove=True)
        self.app.hg.reload()
        with self.app.test_request_context():
            data = self.app.hg.get('post/foo-bar')
            self.assertFalse(data is None, 'Reload failed. Commited stuff ' \
                             'wasn\'t reloaded')


class MercurialLoaderTestCase(TestCaseWithNewRepo):

    def test_get_source(self):
        with self.app.test_request_context():
            self.assertRaises(TemplateNotFound,
                              self.app.jinja_loader.get_source,
                              self.app.jinja_env, 'test.html')

        new_file = os.path.join(self.repo_path,
                                self.app.config['TEMPLATES_DIR'], 'test.html')

        with codecs.open(new_file, 'w', encoding='utf-8') as fp:
            fp.write('foo')

        self.app.hg.reload()
        with self.app.test_request_context():
            self.assertRaises(TemplateNotFound,
                              self.app.jinja_loader.get_source,
                              self.app.jinja_env, 'test.html')

        self.app.debug = True
        self.app.hg.reload()
        with self.app.test_request_context():
            contents, filename, up2date = self.app.jinja_loader.get_source(
                self.app.jinja_env, 'test.html')
            self.assertTrue('foo' in contents, 'Invalid template!')
            # TODO: fix and test filename
            self.assertFalse(up2date(), 'up2date failed. It should always ' \
                             'return False when debug is enabled')

        self.app.debug = False
        self.app.hg.reload()
        with self.app.test_request_context():
            contents, filename, up2date = self.app.jinja_loader.get_source(
                self.app.jinja_env, 'test.html')
            self.assertFalse(up2date(), 'up2date failed. Debug disabled. ' \
                             'Before commit.')
            self.commit(message='foo', addremove=True)
            self.app.hg.reload()
            contents, filename, up2date = self.app.jinja_loader.get_source(
                self.app.jinja_env, 'test.html')
            self.assertTrue(up2date(), 'up2date failed. Debug disabled. ' \
                            'After commit.')
            with codecs.open(new_file, 'a', encoding='utf-8') as fp:
                fp.write('bar')
            self.commit(message='bar', addremove=True)
            self.app.hg.reload()
            self.assertFalse(up2date(), 'up2date failed. Debug disabled. ' \
                             'After 2nd commit')

    def test_list_templates(self):
        default_templates_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'templates')
        templates_dir = os.path.join(self.repo_path,
                                     self.app.config['TEMPLATES_DIR'])
        e = _walk(default_templates_dir) + _walk(templates_dir)
        with self.app.test_request_context():
            for f in self.app.jinja_loader.list_templates():
                full_f1 = os.path.join(default_templates_dir, f)
                full_f2 = os.path.join(templates_dir, f)
                self.assertTrue(full_f1 in e or full_f2 in e,
                                'File not found: %s' % f)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HgApiTestCase))
    suite.addTest(unittest.makeSuite(MercurialLoaderTestCase))
    return suite
