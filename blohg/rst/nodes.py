# -*- coding: utf-8 -*-
"""
    blohg.rst.nodes
    ~~~~~~~~~~~~~~~

    Module with the custom blohg reStructuredText doctree nodes.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from docutils.nodes import General, Element


class iframe_flash_video(General, Element):
    pass
