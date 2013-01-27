# -*- coding: utf-8 -*-
"""
    blohg.vcs
    ~~~~~~~~~

    Module with the basic classes for the VCS backends.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from abc import ABCMeta, abstractmethod, abstractproperty


class Repository:

    __metaclass__ = ABCMeta

    def __init__(self, path):
        self.path = path

    @abstractmethod
    def get_changectx(self, revision=None):
        pass

    @abstractmethod
    def create_repo(repo_path):
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
