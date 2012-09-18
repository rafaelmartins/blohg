# -*- coding: utf-8 -*-
"""
    blohg.hgapi.repo
    ~~~~~~~~~~~~~~~~

    Module with the basic classes for the mercurial low-level API.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from mercurial import commands, hg, ui as _ui

STATE_STABLE = 1
STATE_VARIABLE = 2


class RepoStateBase(object):
    """Class that represents a repository state. It provides access to
    everything needed by the blohg internal APIs from the Mercurial API.
    """

    def __init__(self, ui, repo):
        self._ui = ui
        self._repo = repo
        self.revision = self._repo[self.branch]
        self.revno = self.revision.rev()

    @property
    def branch(self):
        raise NotImplementedError

    @property
    def _extra_files(self):
        raise NotImplementedError

    @property
    def files(self):
        files = set(self.revision.manifest().keys())
        try:
            files = files.union(set(self._extra_files))
        except NotImplementedError:
            pass
        return sorted(files)

    def needs_reload(self):
        raise NotImplementedError

    def get_fctx(self, path):
        return self.revision.filectx(path)

    def get(self, path):
        return self.get_fctx(path).data()

    def get_filelog(self, path):
        filelog = self.get_fctx(path).filelog()
        for i in filelog:
            yield self._repo[filelog.linkrev(i)]


class RepoStateStable(RepoStateBase):
    """Class with the specific implementation details for the stable state of
    the repository. It inherits the common implementation from the class
    :class:`RepoStateBase`.
    """

    @property
    def branch(self):
        try:
            return self._repo.branchtags()['default']
        except Exception:
            return None

    def needs_reload(self):
        if self.revno is None:
            return True
        repo = hg.repository(self._ui, self._repo.root)
        revision = repo[self.branch]
        return revision.rev() > self.revno


class RepoStateVariable(RepoStateBase):
    """Class with the specific implementation details for the variable state of
    the repository. It inherits the common implementation from the class
    :class:`RepoStateBase`.
    """

    branch = None

    @property
    def _extra_files(self):
        return self._repo.status(unknown=True)[4]

    def needs_reload(self):
        """This state is mainly used by the command-line tool, and didn't
        provides any reliable way to evaluate its "freshness". Always reload.
        """
        return True


class Repository(object):
    """The main class to provide low-level access to a blohg-aware Mercurial
    repository.
    """

    def __init__(self, path, ui=None):
        self.path = path
        self.ui = ui or _ui.ui()
        self._repo = hg.repository(self.ui, self.path)

    def get_repostate(self, state=STATE_STABLE):
        """blohg supports 2 repository states.

        - stable: default state, includes all the files that are tracked by
                  mercurial, from the top of the 'default' branch.
        - variable: includes all the files in the mercurial repository
                    directory, even the untracked ones, excluding the
                    .hgignore'd files.

        States are represented by instances of classes
        (:class:`RepoStateStable` and :class:`RepoStateVariable`), that
        provides access to everything related to the repository, filtered by
        the state, like: list of files, content of files, etc. The repository
        state object will be used later by the parsers to generate content
        suitable for publishing.
        """

        if state == STATE_STABLE:
            return RepoStateStable(self.ui, self._repo)
        elif state == STATE_VARIABLE:
            return RepoStateVariable(self.ui, self._repo)
        raise RuntimeError('Invalid repository state: %r' % state)

    def add(self, *pats, **opts):
        return commands.add(self.ui, self._repo, *pats, **opts)

    def commit(self, *pats, **opts):
        return commands.commit(self.ui, self._repo, *pats, **opts)
