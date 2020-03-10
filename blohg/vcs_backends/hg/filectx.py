# -*- coding: utf-8 -*-
"""
    blohg.vcs_backends.hg.filectx
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Model with classes to represent Mercurial file context.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import time
from flask.helpers import locked_cached_property
from blohg.vcs_backends.hg.utils import hg2u, u2hg

from blohg.vcs import FileCtx as _FileCtx


class FileCtx(_FileCtx):
    """Base class that represents a file context."""

    def __init__(self, repo, changectx, path):
        self._repo = repo
        self._changectx = changectx
        self._path = path
        self._ctx = self._changectx[u2hg(self._path)]

    @locked_cached_property
    def _first_changeset(self):
        filelog = self._ctx.filelog()
        if len(list(filelog)) > 0:
            return self._repo[filelog.linkrev(0)]

    @locked_cached_property
    def path(self):
        """UTF-8 encoded file path, relative to the repository root."""
        return hg2u(self._ctx.path())

    @locked_cached_property
    def data(self):
        """Raw data of the file."""
        return self._ctx.data()

    @locked_cached_property
    def content(self):
        """UTF-8 encoded content of the file."""
        return hg2u(self.data)

    @locked_cached_property
    def date(self):
        """Unix timestamp of the creation date of the file (date of the first
        commit).
        """
        if self._first_changeset:
            return int(self._first_changeset.date()[0])
        return int(time.time())

    @locked_cached_property
    def mdate(self):
        """Unix timestamp of the last modification date of the file (date of
        the most recent commit).
        """
        filelog = self._ctx.filelog()
        changesets = list(filelog)
        if len(changesets) > 1:
            last_changeset = self._repo[filelog.linkrev(len(changesets) - 1)]
            return int(last_changeset.date()[0])

    @locked_cached_property
    def author(self):
        """The creator of the file (commiter of the first revision of the
        file)."""
        if self._first_changeset:
            return hg2u(self._first_changeset.user())
        try:
            return hg2u(self._ctx.user())
        except:
            pass
