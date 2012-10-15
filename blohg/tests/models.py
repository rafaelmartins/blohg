# -*- coding: utf-8 -*-
"""
    blohg.tests.models
    ~~~~~~~~~~~~~~~~~~

    Module with tests for blohg models.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import codecs
import time
import unittest
import os
from datetime import datetime
from mercurial import commands, hg, ui
from shutil import rmtree
from tempfile import mkdtemp

from blohg import create_app
from blohg.hg.filectx import FileCtx
from blohg.models import Page, Post
from blohg.utils import create_repo


SAMPLE_PAGE = """\
My sample page
==============

First paragraph.

This is my abstract.

.. read_more

This is the content of the page

"""

SAMPLE_POST = """\
My sample post
==============

.. tags: xd, lol,hehe

First paragraph.

This is my post abstract.

.. read_more

This is the content of the post

"""


class PageTestCase(unittest.TestCase):

    content = SAMPLE_PAGE
    model = Page

    def setUp(self):
        self.repo_path = mkdtemp()
        self.ui = ui.ui()
        self.ui.setconfig('ui', 'username', 'foo <foo@bar.com>')
        self.ui.setconfig('ui', 'quiet', True)
        commands.init(self.ui, self.repo_path)
        self.repo = hg.repository(self.ui, self.repo_path)

    def tearDown(self):
        try:
            rmtree(self.repo_path)
        except:
            pass

    def _get_model(self, content):
        file_dir = os.path.join(self.repo_path, 'content')
        file_path = os.path.join(file_dir, 'stub.rst')
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)
        with codecs.open(file_path, 'w', encoding='utf-8') as fp:
            fp.write(content)
        commands.commit(self.ui, self.repo, file_path, message='foo',
                        addremove=True)
        ctx = FileCtx(self.repo, self.repo[None], 'content/stub.rst')
        return self.model(ctx, 'content', '.rst', 2)

    def test_abstract(self):
        obj = self._get_model(self.content)
        search_abstract = 'abstract.'
        search_full = 'This is the content of the'
        self.assertTrue(search_abstract in obj.abstract)
        self.assertTrue(search_abstract in obj.abstract_html)
        self.assertTrue(search_abstract in obj.abstract_raw_html)
        self.assertFalse(search_full in obj.abstract)
        self.assertFalse(search_full in obj.abstract_html)
        self.assertFalse(search_full in obj.abstract_raw_html)

    def test_fulltext(self):
        obj = self._get_model(self.content)
        search_abstract = 'abstract.'
        search_full = 'This is the content of the'
        self.assertTrue(search_abstract in obj.abstract)
        self.assertTrue(search_abstract in obj.abstract_html)
        self.assertTrue(search_abstract in obj.abstract_raw_html)
        self.assertTrue(search_full in obj.full)
        self.assertTrue(search_full in obj.full_html)
        self.assertTrue(search_full in obj.full_raw_html)

    def test_date_and_mdate(self):
        obj = self._get_model(self.content)
        self.assertTrue(obj.date <= time.time())
        self.assertTrue(obj.datetime <= datetime.utcnow())
        self.assertTrue(obj.mdate is None)
        self.assertTrue(obj.mdatetime is None)
        self.assertTrue(isinstance(obj.date, int))
        self.assertTrue(isinstance(obj.datetime, datetime))

        old_date = obj.date
        old_datetime = obj.datetime

        # force date
        content = self.content + """\
.. date: 1234567890
"""
        obj = self._get_model(content)
        self.assertEqual(obj.date, 1234567890)
        self.assertEqual(obj.datetime, datetime(2009, 2, 13, 23, 31, 30))
        self.assertTrue(obj.mdate >= old_date)
        self.assertTrue(obj.mdatetime >= old_datetime)

        # force date and mdate
        content = self.content + """\
.. date: 1234567890
.. mdate: 1234567891
"""
        obj = self._get_model(content)
        self.assertEqual(obj.mdate, 1234567891)
        self.assertEqual(obj.mdatetime, datetime(2009, 2, 13, 23, 31, 31))

    def test_author_default(self):
        obj = self._get_model(self.content)
        self.assertEqual(obj.author_name, 'foo')
        self.assertEqual(obj.author_email, 'foo@bar.com')

    def test_author_without_email(self):
        content = self.content + """\
.. author: john
"""
        obj = self._get_model(content)
        self.assertEqual(obj.author_name, 'john')
        self.assertTrue(obj.author_email is None)

    def test_author_explicit(self):
        content = self.content + """\
.. author: john <example@example.org>
"""
        obj = self._get_model(content)
        self.assertEqual(obj.author_name, 'john')
        self.assertEqual(obj.author_email, 'example@example.org')

    def test_path(self):
        obj = self._get_model(self.content)
        self.assertEqual(obj.path, 'content/stub.rst')

    def test_slug(self):
        obj = self._get_model(self.content)
        self.assertEqual(obj.slug, 'stub')

    def test_title(self):
        obj = self._get_model(self.content)
        self.assertTrue(obj.title.startswith('My sample '))

    def test_description(self):
        obj = self._get_model(self.content)
        self.assertEqual(obj.description, 'First paragraph.')

    def test_aliases(self):
        obj = self._get_model(self.content)
        self.assertEqual(obj.aliases, [])

    def test_aliases_explicit(self):
        content = self.content + """\
.. aliases: 301:/my-old-post-location/,/another-old-location/
"""
        obj = self._get_model(content)
        self.assertEqual(obj.aliases, [(301, '/my-old-post-location/'),
                                       (302, '/another-old-location/')])


class PostTestCase(PageTestCase):

    content = SAMPLE_POST
    model = Post

    def test_tags(self):
        obj = self._get_model(self.content)
        self.assertEqual(obj.tags, ['xd', 'lol', 'hehe'])


class HgTestCase(unittest.TestCase):

    def setUp(self):
        self.repo_path = mkdtemp()
        self.ui = ui.ui()
        self.ui.setconfig('ui', 'quiet', True)
        self.ui.setconfig('ui', 'username', 'foo <foo@bar.com>')
        create_repo(self.repo_path, self.ui)
        self.app = create_app(self.repo_path, self.ui)
        self.app.config['REPO_PATH'] = self.repo_path
        self.repo = hg.repository(self.ui, self.repo_path)
        commands.commit(self.ui, self.repo, message='foo', addremove=True)

    def tearDown(self):
        try:
            rmtree(self.repo_path)
        except:
            pass
