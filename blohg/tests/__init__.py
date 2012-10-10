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
from blohg.tests.models import HgTestCase, PageTestCase, PostTestCase

#from blohg.tests.hgapi import HgApiTestCase
#from blohg.tests.hgapi.models import PageTestCase, PostTestCase
#from blohg.tests.hgapi.repo import RepositoryTestCase, \
#     RepoStateStableTestCase, RepoStateVariableTestCase
#from blohg.tests.hgapi.templates import MercurialLoaderTestCase
from blohg.tests.utils import UtilsTestCase


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HgRepositoryTestCase))
    suite.addTest(unittest.makeSuite(ChangeCtxDefaultTestCase))
    suite.addTest(unittest.makeSuite(ChangeCtxWorkingDirTestCase))
    suite.addTest(unittest.makeSuite(FileCtxTestCase))
    suite.addTest(unittest.makeSuite(PageTestCase))
    suite.addTest(unittest.makeSuite(PostTestCase))
    suite.addTest(unittest.makeSuite(HgTestCase))
    suite.addTest(unittest.makeSuite(AppTestCase))

    #suite.addTest(unittest.makeSuite(HgApiTestCase))
    suite.addTest(unittest.makeSuite(UtilsTestCase))
    #suite.addTest(unittest.makeSuite(MercurialLoaderTestCase))
    #suite.addTest(unittest.makeSuite(RepoStateStableTestCase))
    #suite.addTest(unittest.makeSuite(RepoStateVariableTestCase))
    #suite.addTest(unittest.makeSuite(RepositoryTestCase))

    return suite
