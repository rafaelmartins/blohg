# -*- coding: utf-8 -*-
"""
    blohg.tests.rst_parser.directives
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Package with tests for the custom blohg reStructuredText directives.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import unittest
from docutils.parsers.rst.directives import _directives, register_directive

from blohg.rst_parser import parser
from blohg.rst_parser.directives import Vimeo, Youtube, SourceCode, Math


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
