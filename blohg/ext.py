# -*- coding: utf-8 -*-
"""
    blohg.ext
    ~~~~~~~~~

    Blohg support for 3rd-party extensions.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from flask.ctx import _RequestGlobals, _app_ctx_stack


class BlohgExtension(object):

    def __init__(self, import_name):
        self.import_name = import_name
        # id is used as prefix for most of the extension-related stuff naming
        self.ext_id = self.import_name.replace('.', '_')
        self._callbacks = []
        self._register_extension()

    @property
    def g(self):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            key = self.ext_id + '_globals'
            if not hasattr(ctx, key):
                setattr(ctx, key, _RequestGlobals())
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
