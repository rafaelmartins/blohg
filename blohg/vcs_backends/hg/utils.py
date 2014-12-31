# -*- coding: utf-8 -*-
"""
    blohg.vcs_backends.hg.utils
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Mercurial related utils

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from mercurial import encoding


def hg2u(s):
    """Returns a unicode object representing the mercurial string."""
    return encoding.fromlocal(s).decode("utf-8")


def u2hg(s):
    """Returns a mercurial string representing an unicode object."""
    return encoding.tolocal(s.encode("utf-8"))
