# -*- coding: utf-8 -*-
"""
    blohg.rst
    ~~~~~~~~~

    Package with reStructuredText-related stuff needed by blohg, like directives
    and roles.

    :copyright: (c) 2010-2011 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from docutils.core import publish_parts
from docutils.parsers.rst.directives import register_directive
from docutils.parsers.rst.roles import register_local_role

from blohg.rst.directives import __directives__
from blohg.rst.roles import __roles__

# registering docutils' directives
for directive in __directives__:
    register_directive(directive, __directives__[directive])

# registering docutils' roles
for role in __roles__:
    register_local_role(role, __roles__[role])


def parser(content):
    parts = publish_parts(source=content, writer_name='html4css1',
                          settings_overrides={'input_encoding': 'utf-8',
                                              'output_encoding': 'utf-8',
                                              'initial_header_level': 3})
    return {'title': parts['title'], 'fragment': parts['fragment']}
