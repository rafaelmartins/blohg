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
import unittest
from jinja2.loaders import ChoiceLoader
from jinja2.exceptions import TemplateNotFound
from mercurial import hg, ui
from mercurial.commands import add, commit, rollback, revert
from shutil import rmtree
from tempfile import mkdtemp

from blohg import create_app
from blohg.utils import create_repo


class TestCaseWithNewRepo(unittest.TestCase):

    def setUp(self):
        self.repo_path = mkdtemp()
        create_repo(create_app(self.repo_path))
        self.ui = ui.ui()
        self.ui.setconfig('ui', 'quiet', True)
        os.environ['HGUSER'] = 'foo <foo@bar.com>'
        self.repo = hg.repository(self.ui, self.repo_path)
        add(self.ui, self.repo)

    def tearDown(self):
        try:
            rmtree(self.repo_path)
            del os.environ['HGUSER']
        except:
            pass

    def walk(self, p):
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


class HgApiTestCase(TestCaseWithNewRepo):

    def test_repo_structure(self):
        e = self.walk(self.repo_path)
        for f in [os.path.join('content', 'attachments', 'mercurial.png'),
                  os.path.join('content', 'post', 'example-post.rst'),
                  os.path.join('content', 'post', 'lorem-ipsum.rst'),
                  os.path.join('content', 'about.rst'),
                  os.path.join('static', 'screen.css'),
                  os.path.join('templates', 'base.html'),
                  os.path.join('templates', 'posts.html'),
                  os.path.join('templates', 'post_list.html'),
                  'config.yaml', '.hgignore']:
            full_f = os.path.join(self.repo_path, f)
            size_f = os.stat(full_f).st_size
            assert full_f in e, 'File not found: ' + f
            assert size_f > 0, 'Empty file: ' + f

    def test_setup_mercurial(self):
        app = create_app(self.repo_path)
        assert hasattr(app, 'hg'), 'mercurial not setup.'
        assert isinstance(app.jinja_loader, ChoiceLoader), \
               'Invalid Jinja2 loader.'

    def test_get_page(self):
        app = create_app(self.repo_path)
        with app.test_request_context():
            data = app.hg.get('about')
            assert data is not None, 'Page not found: about'
            assert 'About me' in data.title, 'Failed to parse the title'
            assert '<img' in data.full_html, 'reStructuredText parser failed'
            assert data.path == 'content/about.rst', 'Invalid path'
            assert data.slug == 'about', 'Failed to parse the slug'
            assert data.author_name == 'foo', 'Failed to parse author name'
            assert data.author_email == 'foo@bar.com', 'Failed to parse ' \
                   'author email'

            # TODO: test aliases

    def test_get_post(self):
        app = create_app(self.repo_path)
        with app.test_request_context():
            data = app.hg.get('post/lorem-ipsum')
            assert data is not None, 'Page not found: post/lorem-ipsum'
            assert 'lorem-ipsum' in data.tags, 'Failed to parse the tags'

    def test_reload(self):
        app = create_app(self.repo_path)

        with app.test_request_context():
            data = app.hg.get('post/foo-bar')
            assert data is None, 'New post found before created! ' \
                   'Run to the hills :P'

        new_file = os.path.join(self.repo_path, 'content', 'post',
                                'foo-bar.rst')
        with codecs.open(new_file, 'w', encoding='utf-8') as fp:
            fp.write(os.linesep.join(['Foo', '---', '', 'Bar']))
        add(self.ui, self.repo, new_file)

        app.hg.reload()
        with app.test_request_context():
            data = app.hg.get('post/foo-bar')
            assert data is None, 'Reload failed. Uncommited stuff was ' \
                   'reloaded, with debug disabled'

        app.debug = True
        app.hg.reload()
        with app.test_request_context():
            data = app.hg.get('post/foo-bar')
            assert data is not None, 'Reload failed. Uncommited stuff ' \
                   'wasn\'t reloaded, with debug enabled'

        app.debug = False
        commit(self.ui, self.repo, message='foo')
        app.hg.reload()
        with app.test_request_context():
            data = app.hg.get('post/foo-bar')
            assert data is not None, 'Reload failed. Commited stuff wasn\'t ' \
                   'reloaded'
        os.unlink(new_file)
        rollback(self.ui, self.repo)
        revert(self.ui, self.repo, all=True, no_backup=True)


class MercurialLoaderTestCase(TestCaseWithNewRepo):

    def test_get_source(self):
        app = create_app(self.repo_path)

        with app.test_request_context():
            self.assertRaises(TemplateNotFound, app.jinja_loader.get_source,
                              app.jinja_env, 'test.html')

        new_file = os.path.join(self.repo_path, app.config['TEMPLATES_DIR'],
                                'test.html')

        with codecs.open(new_file, 'w', encoding='utf-8') as fp:
            fp.write('foo')
        add(self.ui, self.repo, new_file)

        app.hg.reload()
        with app.test_request_context():
            self.assertRaises(TemplateNotFound, app.jinja_loader.get_source,
                              app.jinja_env, 'test.html')

        app.debug = True
        app.hg.reload()
        with app.test_request_context():
            contents, filename, up2date = app.jinja_loader.get_source(
                app.jinja_env, 'test.html')
            assert 'foo' in contents, 'Invalid template!'
            # TODO: fix and test filename
            assert not up2date(), 'up2date failed. It should always return ' \
                   'False when debug is enabled'

        app.debug = False
        app.hg.reload()
        with app.test_request_context():
            contents, filename, up2date = app.jinja_loader.get_source(
                app.jinja_env, 'test.html')
            assert not up2date(), 'up2date failed. Debug disabled. Before ' \
                   'commit.'
            commit(self.ui, self.repo, message='foo')
            app.hg.reload()
            contents, filename, up2date = app.jinja_loader.get_source(
                app.jinja_env, 'test.html')
            assert up2date(), 'up2date failed. Debug disabled. After commit.'
            with codecs.open(new_file, 'a', encoding='utf-8') as fp:
                fp.write('bar')
            commit(self.ui, self.repo, message='bar')
            app.hg.reload()
            assert not up2date(), 'up2date failed. Debug disabled. After ' \
                   '2nd commit'

        # half-ass cleanup :(
        os.unlink(new_file)
        revert(self.ui, self.repo, all=True, no_backup=True, rev=0)
        commit(self.ui, self.repo, message='revert')

    def test_list_templates(self):
        app = create_app(self.repo_path)
        default_templates_dir = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'templates')
        templates_dir = os.path.join(self.repo_path,
                                     app.config['TEMPLATES_DIR'])
        e = self.walk(default_templates_dir) + self.walk(templates_dir)
        with app.test_request_context():
            for f in app.jinja_loader.list_templates():
                full_f1 = os.path.join(default_templates_dir, f)
                full_f2 = os.path.join(templates_dir, f)
                if full_f1 in e:
                    full_f = full_f1
                elif full_f2 in e:
                    full_f = full_f2
                else:
                    assert False, 'File not found: ' + f
                size_f = os.stat(full_f).st_size
                assert size_f > 0, 'Empty file: ' + f


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HgApiTestCase))
    suite.addTest(unittest.makeSuite(MercurialLoaderTestCase))
    return suite
