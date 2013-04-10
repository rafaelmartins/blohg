# -*- coding: utf-8 -*-
"""
    blohg.signals
    ~~~~~~~~~~~~~

    Blohg signals declaration.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from blinker import Namespace

signals = Namespace()

reloaded = signals.signal('reloaded')
