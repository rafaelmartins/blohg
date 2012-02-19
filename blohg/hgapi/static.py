# -*- coding: utf-8 -*-
"""
    blohg.hgapi.static
    ~~~~~~~~~~~~~~~~~~

    Module with stuff to deal with static files from Mercurial repositories.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from flask import current_app, request, abort
from time import time
from zlib import adler32

import posixpath
import mimetypes


class MercurialStaticFile(object):
    """Callable to create a Response object for static files loaded from
    the current Mercurial repository.
    """

    def __init__(self, config_key):
        self._config_key = config_key

    def __call__(self, filename):
        directory = current_app.config[self._config_key]
        filename = posixpath.join(directory, filename)
        mimetype = mimetypes.guess_type(filename)[0]
        if mimetype is None:
            mimetype = 'application/octet-stream'
        try:
            filectx = current_app.hg.revision[filename]
            data = filectx.data()
        except:
            abort(404)
        rv = current_app.response_class(data, mimetype=mimetype,
            direct_passthrough=True)
        rv.cache_control.public = True
        cache_timeout = 60 * 60 * 12
        rv.cache_control.max_age = cache_timeout
        rv.expires = int(time() + cache_timeout)
        try:
            date = int(filectx.date()[0])
        except:
            date = time()
        rv.set_etag('blohg-%s-%s-%s' % (date, len(data), adler32(filename) \
            & 0xffffffff))
        return rv.make_conditional(request)
