# -*- coding: utf-8 -*-
"""
    blohg.git.changectx
    ~~~~~~~~~~~~~~~~~~~

    Model with classes to represent Git change context.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import time
from flask.helpers import locked_cached_property
from pygit2 import Repository, GIT_OBJ_BLOB, GIT_OBJ_TREE
from zlib import adler32

from blohg.git.filectx import FileCtx
from blohg.vcs import ChangeCtx


class ChangeCtxDefault(ChangeCtx):
    """Class with the specific implementation details for the change context
    of the default revision state of the repository. It inherits the common
    implementation from the class :class:`ChangeCtxBase`.
    """

    def __init__(self, repo_path):
        self._repo_path = repo_path
        self._repo = Repository(self._repo_path)
        self._ctx = self._repo[self.revision_id]

    @locked_cached_property
    def files(self):
        def r(_files, tree, prefix=None):
            for entry in tree:
                obj = entry.to_object()
                filename = prefix and (prefix + '/' + entry.name) or entry.name
                if obj.type == GIT_OBJ_TREE:
                    r(_files, obj, filename)
                elif obj.type == GIT_OBJ_BLOB:
                    _files.append(filename)
                else:
                    raise RuntimeError('Invalid object: %s' % filename)
        f = []
        r(f, self._ctx.tree)
        return sorted(f)

    @locked_cached_property
    def revision_id(self):
        """This property should be cached because the lookup_reference method
        reloads itself.
        """
        try:
            ref = self._repo.lookup_reference('refs/heads/master')
        except Exception:
            raise RuntimeError('Branch "master" not found!')
        return ref.oid

    def needs_reload(self):
        try:
            ref = self._repo.lookup_reference('refs/heads/master')
        except Exception:
            return True
        return self.revision_id != ref.oid

    def filectx_needs_reload(self, filectx):
        try:
            ref = self._repo.lookup_reference('refs/heads/master')
        except Exception:
            raise RuntimeError('Branch "master" not found!')
        return filectx._changectx.oid != ref.oid

    def published(self, date, now):
        return date <= now

    def etag(self, filectx):
        return 'blohg-%i-%i-%s' % (filectx.mdate or filectx.date,
                                   len(filectx.data), adler32(filectx.path)
                                   & 0xffffffff)

    def get_filectx(self, path):
        return FileCtx(self._repo, self._ctx, path)


class ChangeCtxWorkingDir(ChangeCtxDefault):
    """Class with the specific implementation details for the change context
    of the working dir of the repository. It inherits the common implementation
    from the class :class:`ChangeCtxBase`.
    """

    @locked_cached_property
    def revision_id(self):
        return self._repo.head.oid

    @locked_cached_property
    def files(self):
        return [entry.path for entry in self._repo.index]

    def needs_reload(self):
        """This change context is mainly used by the command-line tool, and
        didn't provides any reliable way to evaluate its "freshness". Always
        reload.
        """
        return True

    def filectx_needs_reload(self, filectx):
        return True

    def published(self, date, now):
        return True

    def etag(self, filectx):
        return 'blohg-%i-%i-%s' % (time.time(), len(filectx.data),
                                   adler32(filectx.path) & 0xffffffff)

    def get_filectx(self, path):
        return FileCtx(self._repo, self._ctx, path, use_index=True)
