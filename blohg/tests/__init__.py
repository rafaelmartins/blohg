# -*- coding: utf-8 -*-
"""
    blohg.tests
    ~~~~~~~~~~~

    Main unit test package.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import unittest

from blohg.tests.app import AppTestCase
from blohg.tests.hg import HgRepositoryTestCase
from blohg.tests.hg.changectx import ChangeCtxDefaultTestCase, \
     ChangeCtxWorkingDirTestCase
from blohg.tests.hg.filectx import FileCtxTestCase
from blohg.tests.models import BlogTestCase, PageTestCase, PostTestCase
from blohg.tests.templating import BlohgLoaderTestCase
from blohg.tests.utils import UtilsTestCase


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AppTestCase))
    suite.addTest(unittest.makeSuite(HgRepositoryTestCase))
    suite.addTest(unittest.makeSuite(ChangeCtxDefaultTestCase))
    suite.addTest(unittest.makeSuite(ChangeCtxWorkingDirTestCase))
    suite.addTest(unittest.makeSuite(FileCtxTestCase))
    suite.addTest(unittest.makeSuite(BlogTestCase))
    suite.addTest(unittest.makeSuite(PageTestCase))
    suite.addTest(unittest.makeSuite(PostTestCase))
    suite.addTest(unittest.makeSuite(BlohgLoaderTestCase))
    suite.addTest(unittest.makeSuite(UtilsTestCase))
    return suite
