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

from jinja2.loaders import BaseLoader, TemplateNotFound, split_template_path


class MercurialLoader(BaseLoader):
    """A Jinja2 loader that loads templates from a Mercurial repository"""

    def __init__(self, app):
        self.app = app

    def get_source(self, environment, template):
        pieces = split_template_path(template)
        templates_dir = self.app.config['TEMPLATES_DIR']
        filename = posixpath.join(templates_dir, *pieces)
        if filename in self.app.hg.ctx.files:
            filectx = self.app.hg.ctx.get_filectx(filename)
            def up2date():
                if self.app.hg.ctx is None:
                    return False
                needs_reload = self.app.hg.ctx.needs_reload()
                if needs_reload:  # if a reload is required, let's do it!
                    self.app.hg.reload()
                return not needs_reload
            return filectx.content, os.path.join(templates_dir, *pieces), \
                   up2date
        raise TemplateNotFound(template)

    def list_templates(self):
        templates_dir = self.app.config['TEMPLATES_DIR'].strip(os.linesep)
        return sorted([i[len(templates_dir) + 1:] for i in \
                       self.app.hg.ctx.files \
                       if i.startswith(templates_dir + '/')])
