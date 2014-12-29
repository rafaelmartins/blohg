# -*- coding: utf-8 -*-
"""
    blohg.tests.rst_parser.directives
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Module with tests for the custom blohg reStructuredText directives.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import mock
import unittest
from docutils.parsers.rst.directives import _directives, register_directive

from blohg.rst_parser import parser
from blohg.rst_parser.directives import Vimeo, Youtube, SourceCode, Math, \
     AttachmentImage, AttachmentFigure, SubPages, IncludeHg


class DirectiveTestCase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.name = 'blohg-%s' % self.directive.__name__.lower()
        register_directive(self.name, self.directive)

    def tearDown(self):
        # FIXME: do not use the internal list directly (?)
        del _directives[self.name]
        unittest.TestCase.tearDown(self)


class VimeoTestCase(DirectiveTestCase):

    directive = Vimeo

    def test_run_with_default_opts(self):
        content = parser('''\
asd
---

.. blohg-vimeo:: 34368016
''', 3)
        self.assertIn('http://player.vimeo.com/video/34368016',
                      content['fragment'])
        self.assertIn('width: 425px', content['fragment'])
        self.assertIn('height: 344px', content['fragment'])
        self.assertIn('align-center', content['fragment'])
        self.assertIn('frameborder="0"', content['fragment'])
        self.assertIn('allowfullscreen', content['fragment'])

    def test_run(self):
        content = parser('''\
asd
---

.. blohg-vimeo:: 34368016
   :align: left
   :width: 100
   :height: 200
   :allowfullscreen: false
   :border: 1
''', 3)
        self.assertIn('http://player.vimeo.com/video/34368016',
                      content['fragment'])
        self.assertIn('width: 100px', content['fragment'])
        self.assertIn('height: 200px', content['fragment'])
        self.assertIn('align-left', content['fragment'])
        self.assertIn('frameborder="1"', content['fragment'])
        self.assertNotIn('allowfullscreen', content['fragment'])


class YoutubeTestCase(DirectiveTestCase):

    directive = Youtube

    def test_run_with_default_opts(self):
        content = parser('''\
asd
---

.. blohg-youtube:: ssMfQ9ybTEc
''', 3)
        self.assertIn('http://www.youtube.com/embed/ssMfQ9ybTEc',
                      content['fragment'])
        self.assertIn('width: 425px', content['fragment'])
        self.assertIn('height: 344px', content['fragment'])
        self.assertIn('align-center', content['fragment'])
        self.assertIn('frameborder="0"', content['fragment'])
        self.assertIn('allowfullscreen', content['fragment'])

    def test_run(self):
        content = parser('''\
asd
---

.. blohg-youtube:: ssMfQ9ybTEc
   :align: left
   :width: 100
   :height: 200
   :allowfullscreen: false
   :border: 1
''', 3)
        self.assertIn('http://www.youtube.com/embed/ssMfQ9ybTEc',
                      content['fragment'])
        self.assertIn('width: 100px', content['fragment'])
        self.assertIn('height: 200px', content['fragment'])
        self.assertIn('align-left', content['fragment'])
        self.assertIn('frameborder="1"', content['fragment'])
        self.assertNotIn('allowfullscreen', content['fragment'])


class SourceCodeTestCase(DirectiveTestCase):

    directive = SourceCode

    def test_run_with_default_opts(self):
        content = parser('''\
asd
---

.. blohg-sourcecode:: python

    import os

    print os.path

''', 3)
        self.assertIn('class="highlight"', content['fragment'])
        self.assertIn('import', content['fragment'])

    def test_run(self):
        content = parser('''\
asd
---

.. blohg-sourcecode:: python
   :linenos:

    import os

    print os.path

''', 3)
        self.assertIn('class="lineno">3', content['fragment'])
        self.assertIn('import', content['fragment'])


class MathTestCase(DirectiveTestCase):

    directive = Math

    def test_run_with_default_opts(self):
        content = parser('''\
asd
---

.. blohg-math::

   \\frac{x^2}{1+x}
''', 3)
        self.assertIn('https://chart.googleapis.com/chart?cht=tx&chl='
                      '%5Cfrac%7Bx%5E2%7D%7B1%2Bx%7D', content['images'])
        self.assertIn('https://chart.googleapis.com/chart?cht=tx&amp;'
                      'chl=%5Cfrac%7Bx%5E2%7D%7B1%2Bx%7D', content['fragment'])
        self.assertIn('align-center', content['fragment'])

    def test_run(self):
        content = parser('''\
asd
---

.. blohg-math::
   :align: left

   \\frac{x^2}{1+x}
''', 3)
        self.assertIn('https://chart.googleapis.com/chart?cht=tx&chl='
                      '%5Cfrac%7Bx%5E2%7D%7B1%2Bx%7D', content['images'])
        self.assertIn('https://chart.googleapis.com/chart?cht=tx&amp;'
                      'chl=%5Cfrac%7Bx%5E2%7D%7B1%2Bx%7D', content['fragment'])
        self.assertIn('align-left', content['fragment'])


class AttachmentImageTestCase(DirectiveTestCase):

    directive = AttachmentImage

    def setUp(self):
        DirectiveTestCase.setUp(self)
        self._current_app = mock.patch('blohg.rst_parser.directives.current_app')
        self.current_app = self._current_app.start()
        self.current_app.config = {'ATTACHMENT_DIR': 'content/att'}
        self.current_app.blohg.changectx.files = ['content/att/foo.jpg']
        self._url_for = mock.patch('blohg.rst_parser.directives.url_for')
        self.url_for = self._url_for.start()
        self.url_for.return_value = 'http://lol/foo.jpg'

    def tearDown(self):
        del self.url_for
        del self.current_app
        self._url_for.stop()
        self._current_app.stop()
        DirectiveTestCase.tearDown(self)

    def test_run_with_default_opts(self):
        content = parser('''\
asd
---

.. blohg-attachmentimage:: foo.jpg
''', 3)
        self.url_for.assert_called_once_with('attachments', filename='foo.jpg',
                                             _external=True)
        self.assertIn('http://lol/foo.jpg', content['images'])
        self.assertIn('src="http://lol/foo.jpg"', content['fragment'])

    def test_run(self):
        content = parser('''\
asd
---

.. blohg-attachmentimage:: foo.jpg
   :align: left
''', 3)
        self.url_for.assert_called_once_with('attachments', filename='foo.jpg',
                                             _external=True)
        self.assertIn('http://lol/foo.jpg', content['images'])
        self.assertIn('src="http://lol/foo.jpg"', content['fragment'])
        self.assertIn('align-left', content['fragment'])

class AttachmentFigureTestCase(DirectiveTestCase):

    directive = AttachmentFigure

    def setUp(self):
        DirectiveTestCase.setUp(self)
        self._current_app = mock.patch('blohg.rst_parser.directives.current_app')
        self.current_app = self._current_app.start()
        self.current_app.config = {'ATTACHMENT_DIR': 'content/att'}
        self.current_app.blohg.changectx.files = ['content/att/foo.jpg']
        self._url_for = mock.patch('blohg.rst_parser.directives.url_for')
        self.url_for = self._url_for.start()
        self.url_for.return_value = 'http://lol/foo.jpg'

    def tearDown(self):
        del self.url_for
        del self.current_app
        self._url_for.stop()
        self._current_app.stop()
        DirectiveTestCase.tearDown(self)

    def test_run_with_default_opts(self):
        content = parser('''\
asd
---

.. blohg-attachmentfigure:: foo.jpg

   asdf lol.

''', 3)
        self.url_for.assert_called_once_with('attachments', filename='foo.jpg',
                                             _external=True)
        self.assertIn('http://lol/foo.jpg', content['images'])
        self.assertIn('src="http://lol/foo.jpg"', content['fragment'])
        self.assertIn('caption">asdf lol.', content['fragment'])

    def test_run(self):
        content = parser('''\
asd
---

.. blohg-attachmentfigure:: foo.jpg
   :align: left

   asdf lol.

''', 3)
        self.url_for.assert_called_once_with('attachments', filename='foo.jpg',
                                             _external=True)
        self.assertIn('http://lol/foo.jpg', content['images'])
        self.assertIn('src="http://lol/foo.jpg"', content['fragment'])
        self.assertIn('caption">asdf lol.', content['fragment'])
        self.assertIn('align-left', content['fragment'])


class SubPagesTestCase(DirectiveTestCase):

    directive = SubPages

    def setUp(self):
        DirectiveTestCase.setUp(self)
        self._current_app = mock.patch('blohg.rst_parser.directives.current_app')
        self.current_app = self._current_app.start()
        self.current_app.config = {'CONTENT_DIR': 'cont', 'POST_EXT': '.rs'}
        # FIXME: find a way to test sorting
        m1 = mock.Mock(slug='foo', title='Foo :)')
        m2 = mock.Mock(slug='bar', title='Bar!')
        m3 = mock.Mock(slug='foo/bar', title='Foo Bar :P')
        m4 = mock.Mock(slug='foo/bar/baz', title='Foo Bar Baz XD')
        m5 = mock.Mock(slug='foo/bar/bad', title='Foo Bar Bad XD')
        m1.get.side_effect = lambda x, y: y
        m2.get.side_effect = lambda x, y: y
        m3.get.side_effect = lambda x, y: y
        m4.get.side_effect = lambda x, y: y
        m5.get.side_effect = lambda x, y: '###asd###'
        self.current_app.blohg.content.get_all.return_value = [m1, m2, m3, m4, m5]
        self._url_for = mock.patch('blohg.rst_parser.directives.url_for')
        self.url_for = self._url_for.start()
        self.url_for.side_effect = lambda endpoint, slug: '/%s/' % slug

    def tearDown(self):
        del self.url_for
        del self.current_app
        self._url_for.stop()
        self._current_app.stop()
        DirectiveTestCase.tearDown(self)

    def test_run_without_argument(self):
        content = parser('''\
asd
---

.. blohg-subpages::
''', 3, ':repo:cont/index.rs')
        self.assertIn('"/foo/"', content['fragment'])
        self.assertIn('>Foo :)<', content['fragment'])
        self.assertIn('"/bar/"', content['fragment'])
        self.assertIn('>Bar!<', content['fragment'])
        self.assertNotIn('"/foo/bar/"', content['fragment'])
        self.assertNotIn('>Foo Bar :P<', content['fragment'])
        self.assertNotIn('"/foo/bar/baz/"', content['fragment'])
        self.assertNotIn('>Foo Bar Baz XD<', content['fragment'])

    def test_run_without_argument_from_subpage(self):
        content = parser('''\
asd
---

.. blohg-subpages::
''', 3, ':repo:cont/foo.rs')
        self.assertNotIn('"/foo/"', content['fragment'])
        self.assertNotIn('>Foo :)<', content['fragment'])
        self.assertNotIn('"/bar/"', content['fragment'])
        self.assertNotIn('>Bar!<', content['fragment'])
        self.assertIn('"/foo/bar/"', content['fragment'])
        self.assertIn('>Foo Bar :P<', content['fragment'])
        self.assertNotIn('"/foo/bar/baz/"', content['fragment'])
        self.assertNotIn('>Foo Bar Baz XD<', content['fragment'])

    def test_run_with_argument(self):
        content = parser('''\
asd
---

.. blohg-subpages:: foo
''', 3)
        self.assertNotIn('"/foo/"', content['fragment'])
        self.assertNotIn('>Foo :)<', content['fragment'])
        self.assertNotIn('"/bar/"', content['fragment'])
        self.assertNotIn('>Bar!<', content['fragment'])
        self.assertIn('"/foo/bar/"', content['fragment'])
        self.assertIn('>Foo Bar :P<', content['fragment'])
        self.assertNotIn('"/foo/bar/baz/"', content['fragment'])
        self.assertNotIn('>Foo Bar Baz XD<', content['fragment'])

    def test_run_with_argument_from_subpage(self):
        content = parser('''\
asd
---

.. blohg-subpages:: foo
''', 3, ':repo:cont/foo/index.rs')
        self.assertNotIn('"/foo/"', content['fragment'])
        self.assertNotIn('>Foo :)<', content['fragment'])
        self.assertNotIn('"/bar/"', content['fragment'])
        self.assertNotIn('>Bar!<', content['fragment'])
        self.assertIn('"/foo/bar/"', content['fragment'])
        self.assertIn('>Foo Bar :P<', content['fragment'])
        self.assertNotIn('"/foo/bar/baz/"', content['fragment'])
        self.assertNotIn('>Foo Bar Baz XD<', content['fragment'])

    def test_run_with_argument_for_subsubpage(self):
        content = parser('''\
asd
---

.. blohg-subpages:: foo/bar
''', 3)
        self.assertNotIn('"/foo/"', content['fragment'])
        self.assertNotIn('>Foo :)<', content['fragment'])
        self.assertNotIn('"/bar/"', content['fragment'])
        self.assertNotIn('>Bar!<', content['fragment'])
        self.assertNotIn('"/foo/bar/"', content['fragment'])
        self.assertNotIn('>Foo Bar :P<', content['fragment'])
        self.assertIn('"/foo/bar/baz/"', content['fragment'])
        self.assertIn('>Foo Bar Baz XD<', content['fragment'])
        self.assertNotIn('>Foo Bar Bad XD<', content['fragment'])
        self.assertIn('"/foo/bar/bad/"', content['fragment'])
        self.assertIn('###asd###', content['fragment'])


class IncludeHgTestCase(DirectiveTestCase):

    directive = IncludeHg

    def setUp(self):
        DirectiveTestCase.setUp(self)
        self._current_app = mock.patch('blohg.file_like.current_app')
        self.current_app = self._current_app.start()
        self.current_app.config = {'ATTACHMENT_DIR': 'content/att'}
        fctx1 = mock.Mock(path='content/inc.rst', content='''\
Included paragraph
------------------

lol

XD
''')
        self.current_app.blohg.changectx.get_filectx.return_value = fctx1

    def tearDown(self):
        del self.current_app
        self._current_app.stop()
        DirectiveTestCase.tearDown(self)

    def test_simple_include(self):
        content = parser('''\
asd
===

hahah

.. blohg-includehg:: content/foo.rst
''', 3)
        self.assertIn('<h3>Included paragraph</h3>', content['fragment'])
        self.assertIn('<p>lol</p>', content['fragment'])
        self.assertIn('<p>XD</p>', content['fragment'])

    def test_include_with_start_and_end(self):
        content = parser('''\
asd
===

hahah

.. blohg-includehg:: content/foo.rst
   :start-line: 3
   :end-line: 4
''', 3)
        self.assertNotIn('<h3>Included paragraph</h3>', content['fragment'])
        self.assertIn('<p>lol</p>', content['fragment'])
        self.assertNotIn('<p>XD</p>', content['fragment'])

    def test_include_literal(self):
        content = parser('''\
asd
===

hahah

.. blohg-includehg:: content/foo.rst
   :literal:
''', 3)
        self.assertIn('\nIncluded paragraph\n', content['fragment'])
        self.assertIn('\nlol\n', content['fragment'])
        self.assertIn('\nXD\n', content['fragment'])
