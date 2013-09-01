# -*- coding: utf-8 -*-
"""
    blohg.tests
    ~~~~~~~~~~~

    Main unit test package.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import unittest

from blohg.tests.app import AppTestCase
from blohg.tests.ext import BlohgBlueprintTestCase, BlohgExtensionTestCase, \
     ExtensionImporterTestCase
from blohg.tests.rst_parser.directives import VimeoTestCase, YoutubeTestCase, \
     SourceCodeTestCase, MathTestCase, AttachmentImageTestCase, \
     AttachmentFigureTestCase, SubPagesTestCase, IncludeHgTestCase
from blohg.tests.vcs_backends.git import GitRepositoryTestCase
from blohg.tests.vcs_backends.git.changectx import ChangeCtxDefaultTestCase \
     as GitChangeCtxDefaultTestCase, ChangeCtxWorkingDirTestCase as \
     GitChangeCtxWorkingDirTestCase
from blohg.tests.vcs_backends.git.filectx import FileCtxTestCase as \
     GitFileCtxTestCase
from blohg.tests.vcs_backends.hg import HgRepositoryTestCase
from blohg.tests.vcs_backends.hg.changectx import ChangeCtxDefaultTestCase, \
     ChangeCtxWorkingDirTestCase
from blohg.tests.vcs_backends.hg.filectx import FileCtxTestCase
from blohg.tests.models import BlogTestCase, PageTestCase, PostTestCase
from blohg.tests.templating import BlohgLoaderTestCase
from blohg.tests.utils import UtilsTestCase
from blohg.tests.vcs import LoadRepoTestCase
from blohg.tests.views import ViewsTestCase


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AppTestCase))
    suite.addTest(unittest.makeSuite(BlohgBlueprintTestCase))
    suite.addTest(unittest.makeSuite(BlohgExtensionTestCase))
    suite.addTest(unittest.makeSuite(ExtensionImporterTestCase))
    suite.addTest(unittest.makeSuite(VimeoTestCase))
    suite.addTest(unittest.makeSuite(YoutubeTestCase))
    suite.addTest(unittest.makeSuite(SourceCodeTestCase))
    suite.addTest(unittest.makeSuite(MathTestCase))
    suite.addTest(unittest.makeSuite(AttachmentImageTestCase))
    suite.addTest(unittest.makeSuite(AttachmentFigureTestCase))
    suite.addTest(unittest.makeSuite(SubPagesTestCase))
    suite.addTest(unittest.makeSuite(IncludeHgTestCase))
    suite.addTest(unittest.makeSuite(GitRepositoryTestCase))
    suite.addTest(unittest.makeSuite(GitChangeCtxDefaultTestCase))
    suite.addTest(unittest.makeSuite(GitChangeCtxWorkingDirTestCase))
    suite.addTest(unittest.makeSuite(GitFileCtxTestCase))
    suite.addTest(unittest.makeSuite(HgRepositoryTestCase))
    suite.addTest(unittest.makeSuite(ChangeCtxDefaultTestCase))
    suite.addTest(unittest.makeSuite(ChangeCtxWorkingDirTestCase))
    suite.addTest(unittest.makeSuite(FileCtxTestCase))
    suite.addTest(unittest.makeSuite(BlogTestCase))
    suite.addTest(unittest.makeSuite(PageTestCase))
    suite.addTest(unittest.makeSuite(PostTestCase))
    suite.addTest(unittest.makeSuite(BlohgLoaderTestCase))
    suite.addTest(unittest.makeSuite(UtilsTestCase))
    suite.addTest(unittest.makeSuite(LoadRepoTestCase))
    suite.addTest(unittest.makeSuite(ViewsTestCase))
    return suite
