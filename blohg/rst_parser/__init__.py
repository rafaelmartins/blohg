# -*- coding: utf-8 -*-
"""
    blohg.rst_parser
    ~~~~~~~~~~~~~~~~

    Package with reStructuredText-related stuff needed by blohg, like
    directives and roles.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from docutils.core import publish_parts
from docutils.parsers.rst.directives import register_directive
from docutils.parsers.rst.roles import register_local_role

from blohg.rst_parser.directives import index as directives_index
from blohg.rst_parser.roles import index as roles_index
from blohg.rst_parser.writer import BlohgWriter

# registering docutils' directives
for directive in directives_index:
    register_directive(directive, directives_index[directive])

# registering docutils' roles
for role in roles_index:
    register_local_role(role, roles_index[role])


def parser(content, rst_header_level, source_path=None):
    settings = {'input_encoding': 'utf-8', 'output_encoding': 'utf-8',
                'initial_header_level': rst_header_level,
                'docinfo_xform': 0, 'field_name_limit': None}
    parts = publish_parts(source=content, source_path=source_path,
                          writer=BlohgWriter(), settings_overrides=settings)
    return {'title': parts['title'], 'fragment': parts['fragment'],
            'first_paragraph_as_text': parts['first_paragraph_as_text'],
            'images': parts['images']}
