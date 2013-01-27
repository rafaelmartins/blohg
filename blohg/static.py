# -*- coding: utf-8 -*-
"""
    blohg.static
    ~~~~~~~~~~~~

    Module with stuff to deal with static files from Mercurial repositories.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from flask import request, abort
from time import time

import posixpath
import mimetypes


class BlohgStaticFile(object):
    """Callable to create a Response object for static files loaded from
    the current Mercurial repository.
    """

    def __init__(self, app, config_key):
        self.app = app
        self.config_key = config_key

    def __call__(self, filename):
        directory = self.app.config[self.config_key]
        filename = posixpath.join(directory, filename)
        mimetype = mimetypes.guess_type(filename)[0]
        if mimetype is None:
            mimetype = 'application/octet-stream'
        try:
            filectx = self.app.blohg.changectx.get_filectx(filename)
            rv = self.app.response_class(filectx.data, mimetype=mimetype,
                                         direct_passthrough=True)
        except Exception:
            abort(404)
        rv.cache_control.public = True
        cache_timeout = 60 * 60 * 12
        rv.cache_control.max_age = cache_timeout
        rv.expires = int(time() + cache_timeout)
        rv.set_etag(self.app.blohg.changectx.etag(filectx))
        return rv.make_conditional(request)
