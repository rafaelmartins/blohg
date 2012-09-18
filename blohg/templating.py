# -*- coding: utf-8 -*-
"""
    blohg.templating
    ~~~~~~~~~~~~~~~~

    Module with stuff to deal with Jinja2 templates from Mercurial
    repositories.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
import posixpath

from flask import current_app
from jinja2.loaders import BaseLoader, TemplateNotFound, split_template_path


class MercurialLoader(BaseLoader):
    """A Jinja2 loader that loads templates from a Mercurial repository"""

    def get_source(self, environment, template):
        pieces = split_template_path(template)
        templates_dir = current_app.config['TEMPLATES_DIR']
        filename = posixpath.join(templates_dir, *pieces)
        if filename in current_app.hg.ctx.files:
            filectx = current_app.hg.ctx.get_filectx(filename)
            contents = filectx.content
            last_revision = \
                current_app.hg.ctx.get_filectx(filename).last_revision

            def up2date():
                if current_app.hg.ctx.revno is None or last_revision == -1:
                    return False
                return last_revision >= \
                       current_app.hg.ctx.get_filectx(filename).last_revision

            return contents, os.path.join(templates_dir, *pieces), up2date
        raise TemplateNotFound(template)

    def list_templates(self):
        templates_dir = current_app.config['TEMPLATES_DIR'].strip(os.linesep)
        return sorted([i[len(templates_dir) + 1:] for i in \
                       current_app.hg.ctx.files \
                       if i.startswith(templates_dir + '/')])
