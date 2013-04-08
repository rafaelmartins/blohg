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

from flask import current_app
from jinja2.loaders import BaseLoader, TemplateNotFound, split_template_path


class BlohgLoader(BaseLoader):
    """A Jinja2 loader that loads templates from a Mercurial repository"""

    def __init__(self, template_folder):
        self.template_folder = template_folder

    def get_source(self, environment, template):
        pieces = split_template_path(template)
        filename = posixpath.join(self.template_folder, *pieces)
        if filename in current_app.blohg.changectx.files:
            filectx = current_app.blohg.changectx.get_filectx(filename)

            def up2date():
                if current_app.blohg.changectx is None:
                    return False
                return not \
                       current_app.blohg.changectx.filectx_needs_reload(filectx)

            return filectx.content, \
                   os.path.join(self.template_folder, *pieces), up2date
        raise TemplateNotFound(template)

    def list_templates(self):
        templates_dir = current_app.template_folder.strip(os.linesep)
        return sorted([i[len(templates_dir) + 1:] for i in \
                       current_app.blohg.changectx.files \
                       if i.startswith(templates_dir + '/')])
