# -*- coding: utf-8 -*-
"""
    blohg.filters
    ~~~~~~~~~~~~~
    
    Module with some filters for the Jinja2 templates.
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from docutils.core import publish_parts
from docutils.parsers.rst.directives import register_directive
from flask import current_app
from jinja2 import Undefined

from blohg import rst_directives


# registering docutils' directives
for directive in rst_directives.__directives__:
    register_directive(directive, rst_directives.__directives__[directive])


def rst2html(rst):
    """Filter that converts reStructuredText to HTML, returning the body
    of the HTML file.
    
    :param rst: the reStructuredText string.
    :return: the HTML body string.
    """
    
    parts = publish_parts(
        source = rst,
        writer_name = 'html4css1',
        settings_overrides = {
            'input_encoding': 'utf-8',
            'output_encoding': 'utf-8',
            'initial_header_level': 3,
        }
    )
    return {
        'title': parts['title'],
        'fragment': parts['fragment'],
    }


def tag_name(tag):
    """Filter that converts a tag identifier to the tag name. The tag
    name is created capitalizing the tag identifier and replacing ``_``
    by whitespaces, or configured on the app.config['TAGS'] dictionary.
    
    :param tag: the tag identifier string.
    :return: the tag name string.
    """
    
    default_tags = current_app.config['TAGS']
    if tag in default_tags:
        return default_tags[tag]
    return tag.capitalize().replace('_', ' ')


def append_title(title, default):
    """Filter that appends a specific title to the default page title.
    
    :param tag: specific title string.
    :param default: default title string.
    :return: new title string.
    """
    
    if isinstance(title, Undefined):
        return default
    return u'%s » %s' % (default, title)
