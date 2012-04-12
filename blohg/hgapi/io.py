# -*- coding: utf-8 -*-
"""
    blohg.hgapi.io
    ~~~~~~~~~~~~~~

    File-like objects for Mercurial.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from flask import current_app

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class MercurialFile(object):
    """A file-like read-only object for mercurial file-context objects.

    Based in {c,}StringIO. Poorly implemented, because we can't inherit classes
    implemented in C libraries, like cStringIO.StringIO.
    """

    def __init__(self, path):
        try:
            self._fctx = current_app.hg.revision[path]
        except:
            # IncludeHg catches IOError
            raise IOError('Failed to read file from repository: %s' % path)
        self._obj = StringIO(self._fctx.data())

    @property
    def name(self):
        return self._fctx.path()

    def __getattr__(self, name):
        return getattr(self._obj, name)
