# -*- coding: utf-8 -*-
"""
    blohg.vcs_backends.git.filectx
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Model with classes to represent Git file context.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
import time
from flask.helpers import locked_cached_property
from pygit2 import GIT_OBJ_BLOB, GIT_SORT_REVERSE, GIT_SORT_TIME, \
    GIT_SORT_TOPOLOGICAL

from blohg.vcs import FileCtx as _FileCtx


class FileCtx(_FileCtx):
    """Base class that represents a file context."""

    def __init__(self, repo, changectx, path, use_index=False):
        self._repo = repo
        self._changectx = changectx
        self._path = path
        self._use_index = use_index
        try:
            oid = self._changectx.oid
        except AttributeError:
            oid = self._changectx.target
        self._ctx = self.get_fileobj_from_basetree(
            self._repo[oid].tree, self._path)
        if not self._ctx or self._ctx.type != GIT_OBJ_BLOB or use_index:
            try:
                self._ctx = self._repo[self._repo.index[self._path].oid]
            except:
                raise RuntimeError('Invalid file: %s' % self._path)

    def get_fileobj_from_basetree(self, basetree, path):
        tree = [basetree]
        for piece in path.split('/'):
            try:
                tree.append(self._repo[tree.pop()[piece].oid])
            except KeyError:
                return None
        return tree.pop()

    @locked_cached_property
    def _first_changeset(self):
        try:
            ref = self._repo.lookup_reference('refs/heads/master')
        except Exception:
            raise RuntimeError('Branch "master" not found!')
        for commit in self._repo.walk(ref.target,
                                      GIT_SORT_TOPOLOGICAL |
                                      GIT_SORT_TIME |
                                      GIT_SORT_REVERSE):
            obj = self.get_fileobj_from_basetree(commit.tree, self._path)
            if obj is not None:
                return commit

    @locked_cached_property
    def _last_changeset(self):
        try:
            ref = self._repo.lookup_reference('refs/heads/master')
        except Exception:
            return
        head = ref.peel()
        for commit in self._repo.walk(ref.target,
                                      GIT_SORT_TOPOLOGICAL |
                                      GIT_SORT_TIME):
            diff = self._repo.diff(head, commit)
            for patch in diff:
                try:
                    new_file_path = patch.delta.new_file.path
                except AttributeError:
                    new_file_path = patch.new_file_path
                if new_file_path == self._path:
                    return head
            head = commit

    @locked_cached_property
    def path(self):
        """UTF-8 encoded file path, relative to the repository root."""
        return self._path

    @locked_cached_property
    def data(self):
        """Raw data of the file."""
        # This hack avoids 'git add'ing files after every edit.
        # File must be added to index once though.
        if self._use_index:
            real_file = os.path.join(self._repo.workdir, self._path)
            if os.path.isfile(real_file):
                with open(real_file, 'rb') as fp:
                    return fp.read()
        return self._ctx.data

    @locked_cached_property
    def content(self):
        """UTF-8 encoded content of the file."""
        return self.data.decode('utf-8')

    @locked_cached_property
    def date(self):
        """Unix timestamp of the creation date of the file (date of the first
        commit).
        """
        try:
            date = self._first_changeset.author.time
        except:
            date = time.time()
        return int(date)

    @locked_cached_property
    def mdate(self):
        """Unix timestamp of the last modification date of the file (date of
        the most recent commit).
        """
        if self._last_changeset and \
           self._last_changeset.oid != self._first_changeset.oid:
            return int(self._last_changeset.author.time)

    @locked_cached_property
    def author(self):
        """The creator of the file (commiter of the first revision of the
        file)."""
        if self._first_changeset:
            name = self._first_changeset.author.name
            email = self._first_changeset.author.email
        else:
            name = self._repo.config['user.name']
            email = self._repo.config['user.email']
        return '%s <%s>' % (name, email)
