# -*- coding: utf-8 -*-
"""
    blohg.utils
    ~~~~~~~~~~~

    Module with general purpose utilities for blohg.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from calendar import timegm
from time import strptime


def parse_date(date):
    """blohg used to accept datetimes formated as UNIX timestamps to override
    the datetimes provided by the Mercurial API, but UNIX timestamps are hard
    to read and guess. This function allows users to write datetimes using a
    more readable format::

        YYYY-MM-DD HH:MM:SS

    UNIX timestamps are still a valid input format.
    """
    if isinstance(date, int):
        return date
    if isinstance(date, basestring):
        if date.isdigit():
            return int(date)
        timetuple = strptime(date, '%Y-%m-%d %H:%M:%S')
        return timegm(timetuple)
    raise TypeError('Invalid type (%s): %r' % (date.__class__.__name__, date))
