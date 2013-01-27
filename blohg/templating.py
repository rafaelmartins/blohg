# -*- coding: utf-8 -*-
"""
    blohg.templating
    ~~~~~~~~~~~~~~~~

    Module with stuff to deal with Jinja2 templates from Mercurial
    repositories.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
import posixpath

from jinja2.loaders import BaseLoader, TemplateNotFound, split_template_path


class BlohgLoader(BaseLoader):
    """A Jinja2 loader that loads templates from a Mercurial repository"""

    def __init__(self, app):
        self.app = app

    def get_source(self, environment, template):
        pieces = split_template_path(template)
        templates_dir = self.app.config['TEMPLATES_DIR']
        filename = posixpath.join(templates_dir, *pieces)
        if filename in self.app.blohg.changectx.files:
            filectx = self.app.blohg.changectx.get_filectx(filename)

            def up2date():
                if self.app.blohg.changectx is None:
                    return False
                return not \
                       self.app.blohg.changectx.filectx_needs_reload(filectx)

            return filectx.content, os.path.join(templates_dir, *pieces), \
                   up2date
        raise TemplateNotFound(template)

    def list_templates(self):
        templates_dir = self.app.config['TEMPLATES_DIR'].strip(os.linesep)
        return sorted([i[len(templates_dir) + 1:] for i in \
                       self.app.blohg.changectx.files \
                       if i.startswith(templates_dir + '/')])
