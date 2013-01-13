# -*- coding: utf-8 -*-
"""
    blohg.hg
    ~~~~~~~~

    Package with all the classes and functions needed to deal with Mercurial's
    low-level API.

    .. warning::

        Mercurial API isn't stable, according with their own wiki
        (http://mercurial.selenic.com/wiki/MercurialApi). This package needs to
        be well tested against new releases of Mercurial.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from blohg.hg.changectx import ChangeCtxDefault, ChangeCtxWorkingDir

REVISION_WORKING_DIR = 1
REVISION_DEFAULT = 2


class HgRepository(object):
    """Main entrypoint for the Mercurial API layer. This class offers abstract
    access to everything needed by blohg from the low-level API.
    """

    def __init__(self, path):
        self.path = path

    def get_changectx(self, revision=REVISION_DEFAULT):
        """Method that returns a change context for a given Revision state.

        blohg supports 2 revision states.

        - default: default revision, includes all the files that are tracked by
                   mercurial, from the top of the 'default' branch.
        - working_dir: includes all the files in the mercurial repository
                       directory, even the untracked ones, excluding the
                       .hgignore'd files.

        Change contexts are represented by instances of classes
        (:class:`ChangeCtxDefault` and :class:`ChangeCtxWorkingDir`), that
        provides access to everything related to the repository, filtered by
        the revision state, like: list of files, content of files, etc. The
        repository state object will be used later by the parsers to generate
        content suitable for publishing.
        """
        if revision == REVISION_DEFAULT:
            return ChangeCtxDefault(self.path)
        elif revision == REVISION_WORKING_DIR:
            return ChangeCtxWorkingDir(self.path)
        raise RuntimeError('Invalid repository revision: %r' % revision)
