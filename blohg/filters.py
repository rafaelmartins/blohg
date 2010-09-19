# -*- coding: utf-8 -*-

from docutils.core import publish_parts
from docutils.parsers.rst.directives import register_directive
from flask import current_app
from jinja2 import Undefined

from blohg import rst_directives

# registering docutils' directives
for directive in rst_directives.__directives__:
    register_directive(directive, rst_directives.__directives__[directive])


def rst2html(rst):
    parts = publish_parts(
        source = rst,
        writer_name = 'html',
        settings_overrides = {
            'input_encoding': 'utf-8',
            'output_encoding': 'utf-8',
            'doctitle_xform': 0,
            'initial_header_level': 3,
        }
    )
    return parts['body']

def tag_name(tag):
    default_tags = current_app.config['TAGS']
    if tag in default_tags:
        return default_tags[tag]
    return tag.capitalize().replace('_', ' ')

def append_title(title, default):
    if type(title) == Undefined:
        return default
    return u'%s » %s' % (default, title)
