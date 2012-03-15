# -*- coding: utf-8 -*-
"""
    blohg.hgapi.templates
    ~~~~~~~~~~~~~~~~~~~~~

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

    def _filerev(self, filectx):
        filelog = filectx.filelog()
        revision_list = list(filelog)
        if len(revision_list) == 0:
            revision_id = 0
        else:
            revision_id = revision_list[-1]
        return filelog.linkrev(revision_id)

    def get_source(self, environment, template):
        pieces = split_template_path(template)
        templates_dir = current_app.config['TEMPLATES_DIR']
        filename = posixpath.join(templates_dir, *pieces)
        if filename in current_app.hg.revision.manifest():
            filectx = current_app.hg.revision[filename]
            contents = filectx.data().decode('utf-8')
            revision = self._filerev(filectx)

            def up2date():
                if current_app.hg.revision.rev() is None or revision == -1:
                    return False
                return revision >= \
                       self._filerev(current_app.hg.revision[filename])

            return contents, os.path.join(templates_dir, *pieces), up2date
        raise TemplateNotFound(template)

    def list_templates(self):
        templates_dir = current_app.config['TEMPLATES_DIR'].strip(os.linesep)
        return sorted([i[len(templates_dir) + 1:] for i in \
                       current_app.hg.revision.manifest() \
                       if i.startswith(templates_dir + '/')])
