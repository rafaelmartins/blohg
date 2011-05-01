# -*- coding: utf-8 -*-
"""
    blohg.rst_roles
    ~~~~~~~~~~~~~~~
    
    Module with the custom blohg reStructuredText roles.
    
    :copyright: (c) 2011 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from docutils.nodes import reference
from flask import url_for

__all__ = ['attachment_role']


def attachment_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """reStructuredText role that creates a Text node with the full url for an
    attachment.
    """
    
    url = url_for('.attachments', filename=text, _external=True)
    return [reference(url, url, refuri=url)], []


__roles__ = {
    'attachment': attachment_role,
}