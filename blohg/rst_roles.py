# -*- coding: utf-8 -*-
"""
    blohg.rst_roles
    ~~~~~~~~~~~~~~~

    Module with the custom blohg reStructuredText roles.

    :copyright: (c) 2011 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from docutils.nodes import reference
from flask import current_app, url_for

import posixpath


__all__ = ['attachment_role']


def attachment_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """reStructuredText role that creates a Text node with the full url for an
    attachment.
    """

    full_path = posixpath.join(current_app.config['ATTACHMENT_DIR'], text)
    if full_path not in list(current_app.hg.revision):
        msg = inliner.reporter.error(
            'Error in "%s" role: File not found: %s.' % (
                name, full_path
            ),
            line=lineno
        )
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]
    url = url_for('.attachments', filename=text, _external=True)
    return [reference(url, url, refuri=url)], []


__roles__ = {
    'attachment': attachment_role,
}
