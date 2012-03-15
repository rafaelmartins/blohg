# -*- coding: utf-8 -*-
"""
    blohg.rst.roles
    ~~~~~~~~~~~~~~~

    Module with the custom blohg reStructuredText roles.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from docutils.nodes import reference, paragraph
from flask import current_app, url_for

import posixpath
import re


__all__ = ['attachment_role', 'page_role']


def attachment_role(name, rawtext, text, lineno, inliner, options={},
                    content=[]):
    """reStructuredText role that creates a Text node with the full url for an
    attachment.
    """
    label = ""
    if '|' in text:
        text, label = text.split('|')
    full_path = posixpath.join(current_app.config['ATTACHMENT_DIR'], text)
    if full_path not in current_app.hg.revision.manifest():
        msg = inliner.reporter.error('Error in "%s" role: File not found: %s.' \
                                     % (name, full_path), line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    url = url_for('attachments', filename=text, _external=True)
    if not label:
        label = url
    return [reference(url, label, refuri=url)], []


# \x00 means the "<" was backslash-escaped
explicit_title_re = re.compile(r'^(.+?)\s*(?<!\x00)<(.*?)>$', re.DOTALL)


def page_role(name, rawtext, text, lineno, inliner, options={}, content={}):
    """reStructuredText role to generate a link to another page/post
    use as :page:`slug`, or :page:`title <slug>`. In the first case, the
    title used will be the one of the post itself.
    """
    title = None
    target = text
    match = explicit_title_re.match(text)
    if match:
        title, target = match.group(1), match.group(2)
    metadata = current_app.hg.get(target)
    if metadata is None:
        if title is not None:
            target = title
        return [paragraph(rawtext, target)], []
    url = url_for('views.content', slug=metadata.slug, _external=True)
    if title is None:
        title = metadata.title
    return [reference(url, title, refuri=url)], []


index = {
    'attachment': attachment_role,
    'page': page_role,
}
