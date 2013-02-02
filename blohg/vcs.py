# -*- coding: utf-8 -*-
"""
    blohg.vcs
    ~~~~~~~~~

    Module with the basic classes for the VCS backends.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
from abc import ABCMeta, abstractmethod, abstractproperty

REVISION_WORKING_DIR, REVISION_DEFAULT = 1, 2


class Repository:

    __metaclass__ = ABCMeta

    def __init__(self, path):
        self.path = path

    @abstractproperty
    def order(self):
        pass

    @abstractproperty
    def identifier(self):
        pass

    @abstractproperty
    def name(self):
        pass

    @abstractmethod
    def get_changectx(self, revision=None):
        pass

    @abstractmethod
    def create_repo(repo_path):
        pass

    @abstractmethod
    def supported(repo_path):
        pass


class ChangeCtx:

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        pass

    @abstractproperty
    def revision_id(self):
        pass

    @abstractproperty
    def files(self):
        pass

    @abstractmethod
    def needs_reload(self):
        pass

    @abstractmethod
    def filectx_needs_reload(self, filectx):
        pass

    @abstractmethod
    def published(self, date, now):
        pass

    @abstractmethod
    def get_filectx(self, path):
        pass

    @abstractmethod
    def etag(self, filectx):
        pass


class FileCtx:

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, repo, changectx, path, **kwargs):
        pass

    @abstractproperty
    def data(self):
        pass

    @abstractproperty
    def content(self):
        pass

    @abstractproperty
    def date(self):
        pass

    @abstractproperty
    def mdate(self):
        pass

    @abstractproperty
    def author(self):
        pass


def _get_backends():
    cwd = os.path.dirname(os.path.abspath(__file__))
    packages = []
    backends_dir = os.path.join(cwd, 'vcs_backends')
    for d in os.listdir(backends_dir):
        if not os.path.isdir(os.path.join(backends_dir, d)):
            continue
        try:
            __import__('blohg.vcs_backends.%s' % d)
        except ImportError:
            pass
    rv = sorted(Repository.__subclasses__(), key=lambda x: x.order)
    if not len(rv):
        raise RuntimeError('No backend found!')
    return rv


backends = _get_backends()
del _get_backends


def load_repo(repo_path):
    for backend in backends:
        if backend.supported(repo_path):
            return backend(repo_path)
