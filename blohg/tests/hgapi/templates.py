# -*- coding: utf-8 -*-
"""
    blohg.tests.hgapi.templates
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Module with tests for blohg integration with jinja2.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import codecs
import os
from jinja2.exceptions import TemplateNotFound
from mercurial import commands

from blohg.tests.utils import TestCaseWithNewRepo, walk


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
        commands.add(self.ui, self.repo)

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
            os.path.abspath(__file__)), '..', '..', 'templates')
        templates_dir = os.path.join(self.repo_path,
                                     self.app.config['TEMPLATES_DIR'])
        e = walk(default_templates_dir) + walk(templates_dir)
        with self.app.test_request_context():
            for f in self.app.jinja_loader.list_templates():
                full_f1 = os.path.join(default_templates_dir, f)
                full_f2 = os.path.join(templates_dir, f)
                self.assertTrue(full_f1 in e or full_f2 in e,
                                'File not found: %s' % f)
