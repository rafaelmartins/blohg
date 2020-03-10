# -*- coding: utf-8 -*-
"""
    blohg.file_like
    ~~~~~~~~~~~~~~~

    File-like objects for Mercurial.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from flask import current_app
from io import StringIO


class BlohgFile(object):
    """A file-like read-only object for mercurial file-context objects.

    Based in {c,}StringIO. Poorly implemented, because we can't inherit classes
    implemented in C libraries, like cStringIO.StringIO.
    """

    def __init__(self, path):
        try:
            self._filectx = current_app.blohg.changectx.get_filectx(path)
        except:
            # IncludeHg catches IOError
            raise IOError('Failed to read file from repository: %s' % path)
        self._obj = StringIO(self._filectx.content)

    @property
    def name(self):
        return self._filectx.path

    def __getattr__(self, name):
        return getattr(self._obj, name)
