# -*- coding: utf-8 -*-
"""
    blohg.tests.hgapi
    ~~~~~~~~~~~~~~~~~

    Module with tests for blohg integration with mercurial.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import codecs
import os
import posixpath
from jinja2.loaders import ChoiceLoader
from mercurial import commands

from blohg.tests.utils import TestCaseWithNewRepo


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
            self.assertEqual(data.description, 'This is an example page!')
            self.assertTrue('mercurial.png' in data.images[0])

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
        commands.add(self.ui, self.repo)

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
