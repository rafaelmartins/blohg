# -*- coding: utf-8 -*-
"""
    blohg.ext
    ~~~~~~~~~

    Blohg support for 3rd-party extensions.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from flask import Blueprint
from flask.ctx import _app_ctx_stack
from flask.helpers import locked_cached_property
from imp import new_module
from jinja2.loaders import FileSystemLoader

from blohg.static import BlohgStaticFile
from blohg.templating import BlohgLoader

import os
import posixpath
import sys


class BlohgBlueprint(Blueprint):

    @locked_cached_property
    def jinja_loader(self):
        if self.template_folder is not None:
            if ':repo:' in self.root_path:  # just load from repo
                root_path = self.root_path[self.root_path.find(':repo:') + 6:]
                return BlohgLoader(posixpath.join(root_path,
                                                  self.template_folder))
            return FileSystemLoader(os.path.join(self.root_path,
                                                 self.template_folder))

    def register(self, app, options, first_registration=False):
        def register_static(state):
            self.repo_static_folder = None
            if self.has_static_folder:
                if ':repo:' in self.root_path:  # just load from repo
                    static_folder = self.static_folder[
                        self.static_folder.find(':repo:') + 6:]
                    endpoint = '%s.static' % state.blueprint.name
                    if endpoint not in state.app.view_functions:
                        raise RuntimeError('Static endpoint not registered yet '
                                           ' for %s!' % state.blueprint.name)
                    state.app.view_functions[endpoint] = \
                        BlohgStaticFile(static_folder)
                    self.repo_static_folder = static_folder
        self.record(register_static)
        return Blueprint.register(self, app, options, first_registration)


class BlohgExtension(object):

    def __init__(self, import_name):
        self.import_name = import_name
        # id is used as prefix for most of the extension-related stuff naming
        self.ext_id = self.import_name.replace('.', '_')
        self._callbacks = []
        self._register_extension()

    @property
    def g(self):
        ctx = _app_ctx_stack.top.app
        if ctx is not None:
            key = '_%s_globals' % self.ext_id
            if not hasattr(ctx, key):
                setattr(ctx, key, ctx.request_globals_class())
            return getattr(ctx, key)
        raise RuntimeError('Failed to initialize plugin globals.')

    def setup_extension(self, f):
        self._callbacks.append(f)
        return f

    def _register_extension(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'extension_registry'):
                ctx.extension_registry = []
            ctx.extension_registry.append(self)
            return
        raise RuntimeError('Failed to initialize extension registry.')

    def _load_extension(self, app):
        for callback in self._callbacks:
            if callable(callback):
                callback(app)


class ExtensionImporter(object):
    """Loader and Finder to import Python plugins from the Mercurial
    repository. Mostly based on:
    https://github.com/mitsuhiko/flask/blob/master/flask/exthook.py

    See PEP 302 for details.
    """

    def __init__(self, changectx, ext_dir):
        self.changectx = changectx
        self.ext_dir = ext_dir

    def __eq__(self, other):
        return self.__class__.__module__ == other.__class__.__module__ and \
               self.__class__.__name__ == other.__class__.__name__

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def new(cls, *args, **kwargs):
        obj = cls(*args, **kwargs)
        sys.meta_path[:] = [x for x in sys.meta_path if obj != x] + [obj]
        return obj

    def module_file(self, fullname):
        fullname = fullname.replace('.', posixpath.sep)
        for path in [posixpath.join(self.ext_dir, fullname + i) \
                     for i in [posixpath.sep + '__init__.py', '.py']]:
            if path in self.changectx.files:
                return path

    def find_module(self, fullname, path=None):
        if not fullname.startswith('blohg_'):  # ...starting with blohg_
            return
        if self.module_file(fullname) is not None:
            return self

    def load_module(self, fullname):
        mod = sys.modules.setdefault(fullname, new_module(fullname))
        mod.__file__ = self.get_filename(fullname)
        mod.__loader__ = self
        if self.is_package(fullname):
            mod.__path__ = [mod.__file__.rsplit(posixpath.sep, 1)[0]]
            mod.__package__ = fullname
        else:
            mod.__package__ = fullname.rpartition('.')[0]
        exec(self.get_code(fullname), mod.__dict__)
        return mod

    def get_fctx(self, fullname):
        filename = self.module_file(fullname)
        if filename is None:
            raise ImportError('Module not found: %s' % fullname)
        return self.changectx.get_filectx(filename)

    def is_package(self, fullname):
        filename = self.get_filename(fullname)
        return filename.endswith(posixpath.sep + '__init__.py')

    def get_code(self, fullname):
        return compile(self.get_source(fullname), self.get_filename(fullname),
                       'exec')

    def get_source(self, fullname):
        return self.get_fctx(fullname).data

    def get_filename(self, fullname):
        filename = self.module_file(fullname)
        if filename is None:
            raise ImportError('Module not found: %s' % fullname)
        return ':repo:%s' % filename  # :repo: is a placeholder
