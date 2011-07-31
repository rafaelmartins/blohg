# -*- coding: utf-8 -*-
"""
    blohg.mercurial_content
    ~~~~~~~~~~~~~~~~~~~~~~~

    Module with Mercurial-related stuff needed by blohg to load posts
    and static pages.

    :copyright: (c) 2010-2011 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
import re
import time
import yaml

from datetime import datetime
from docutils.core import publish_parts
from docutils.parsers.rst.directives import register_directive
from docutils.parsers.rst.roles import register_local_role
from mercurial import hg, ui
from werkzeug.utils import cached_property

from blohg import rst_directives, rst_roles

try:
    from flask import current_app, g
except ImportError:
    current_app = None
    g = None

re_metadata = re.compile(r'\.\. +([a-z]*): (.*)')
re_read_more = re.compile(r'\.\. +read_more')
re_author = re.compile(r'^(?P<name>[^<]*[^ ])( ?<(?P<email>[^<]*)>)?$')


# registering docutils' directives
for directive in rst_directives.__directives__:
    register_directive(directive, rst_directives.__directives__[directive])

# registering docutils' roles
for role in rst_roles.__roles__:
    register_local_role(role, rst_roles.__roles__[role])


def rst2html(rst):
    """Function that converts reStructuredText to HTML, returning the body
    of the HTML file.

    :param rst: the reStructuredText string.
    :return: a dict with the title and the fragment of the generated HTML.
    """

    parts = publish_parts(
        source=rst,
        writer_name='html4css1',
        settings_overrides={
            'input_encoding': 'utf-8',
            'output_encoding': 'utf-8',
            'initial_header_level': 3,
        }
    )
    return {
        'title': parts['title'],
        'fragment': parts['fragment'],
    }


def load_config(app):
    """This function merges the configuration parameters from the YAML
    file with the ``app.config`` object.

    :param app: the application object.
    """

    app.config.update(yaml.load(app.hg.config))

    # debug parameters
    if app.debug:
        if 'GOOGLE_ANALYTICS' in app.config:
            del app.config['GOOGLE_ANALYTICS']
        app.config['DISQUS_DEVELOPER'] = True


def setup_mercurial(app):
    """This function adds a :class:`MercurialContent` instance to an
    application object, as a ``hg`` attribute, and reloads it as needed.

    :param app: the application object.
    """

    @app.before_request
    def before_request():

        # always init the repository
        repo_path = app.config.get('REPO_PATH', '.')
        repo = hg.repository(ui.ui(), repo_path)

        refresh = False

        if app.debug:
            refresh = True

        if not hasattr(app, 'hg'):
            refresh = True

        # If we still don't want a refresh, it seems that we have an app.hg
        # object, then we need to check if it's new enough
        if not refresh:
            # using the 'tip' revision, as we're not debugging, and just
            # want the committed stuff.
            if repo['tip'].rev() != app.hg.repo['tip'].rev():
                refresh = True

        revision_id = None
        if not app.debug:
            revision_id = 'tip'

        if g is not None:
            g.repo = repo[revision_id]

        # refreshing :)
        if refresh:

            # Deleting the app.hg element. Not sure if it's worth :)
            if hasattr(app, 'hg'):
                del app.hg

            app.hg = MercurialContent(repo, revision_id)
            load_config(app)


class MercurialContent(object):
    """Object that represents a blohg Mercurial repository."""

    config_file = 'config.yaml'
    content_dir = 'content'

    def __init__(self, repo, revision_id):
        """Class constructor"""

        self.repo = repo
        self.revision_id = revision_id
        self.revision = repo[revision_id]

        if current_app is not None:
            self.content_dir = current_app.config['CONTENT_DIR']

    @cached_property
    def _pages(self):
        """Method that returns an ordered list with all the pages/posts
        available.

        :return: a list of :class:`Metadata` objects.
        """

        metadata = []
        for filename in self.revision:
            if filename.startswith(self.content_dir + '/') and \
               filename.endswith('.rst'):
                metadata.append(Metadata(self.repo, self.revision[filename]))
        return sorted(metadata, self._compare_by_date)

    def _compare_by_date(self, a, b):
        """Method that compares 2 :class:`Metadata` objects by creation
        date.
        """

        return b.date - a.date

    def get(self, filename):
        """Method that returns a :class:`Metadata` object for a given
        filename.

        :param filename: the file name string.
        :return: a :class:`Metadata` object.
        """

        full_path = os.path.join(self.content_dir, filename + '.rst')
        for page in self._pages:
            if page.path == full_path:
                return page
        return None

    def get_all(self, only_posts=False):
        """Method that returns a list of :class:`Metadata` objects for
        all the available files, ordered by creation date.

        :param only_posts: a boolean that makes the method returns only
                           the available posts for the given locale, not
                           the static pages.
        :return: a list of :class:`Metadata` objects.
        """

        my_posts_dir = os.path.join(self.content_dir, 'post')
        metadata = []
        for page in self._pages:
            if page.path.startswith(self.content_dir) and not only_posts:
                metadata.append(page)
                continue
            if page.path.startswith(my_posts_dir):
                metadata.append(page)
        return metadata

    def get_by_tag(self, tag):
        """Method that returns a list of :class:`Metadata` objects for a
        given list of tag identifier strings.

        :param tag: a list of tag identifier strings.
        :return: a list of :class:`Metadata` objects.
        """

        posts = []
        for post in self.get_all(only_posts=True):
            valid = True
            for _tag in tag:
                if _tag not in post.tags:
                    valid = False
            if valid:
                posts.append(post)
        return posts

    @cached_property
    def tags(self):
        """Method that returns a list of all the available tag identifiers.

        :return: a list of tag identifiers strings.
        """

        tags = []
        for post in self.get_all(only_posts=True):
            for tag in post.tags:
                if tag not in tags:
                    tags.append(tag)
        tags.sort()
        return tags

    @cached_property
    def config(self):
        """Method that returns a string with the content of the config.yaml
        file.

        :return: a string with the content of the configuration file.
        """

        if self.config_file not in list(self.revision):
            raise RuntimeError('Configuration file not found: %r' % \
                self.config_file)
        return self.revision[self.config_file].data()

    def __repr__(self):
        return '<MercurialContent %r>' % self.repo.root


class Metadata(object):
    """Static page/blog post metadata object."""

    _title = None
    _content_dir = 'content'

    def __init__(self, repo, filectx):
        """Class constructor.

        :param repo: a Mercurial repository object (not
                     :class:`MercurialContent`)
        :param filectx: the Mercurial file context of the file.
        """

        if current_app is not None:
            self._content_dir = current_app.config['CONTENT_DIR']

        self._repo = repo
        self._filectx = filectx
        self._filecontent = filectx.data()
        self._vars = {}
        for i in re_metadata.finditer(self._filecontent):
            self._vars[i.group(1)] = i.group(2).decode('utf-8')
        if 'tags' in self._vars:
            self._vars['tags'] = [i.strip() for i in \
                                  self._vars['tags'].split(',')]
        filelog = self._filectx.filelog()
        changesets = list(filelog)
        first_changeset = self._repo[filelog.linkrev(0)]
        if 'date' in self._vars:
            try:
                self._vars['date'] = int(self._vars['date'])
            except ValueError:
                del self._vars['date']
        else:
            self._vars['date'] = int(first_changeset.date()[0])
            if self._vars['date'] == 0:
                self._vars['date'] = int(time.time())
        self._vars['datetime'] = datetime.utcfromtimestamp(self._vars['date'])
        if 'mdate' in self._vars:
            try:
                self._vars['mdate'] = int(self._vars['mdate'])
            except ValueError:
                del self._vars['mdate']
        if 'mdate' not in self._vars and len(changesets) > 1:
            last_changeset = self._repo[filelog.linkrev(len(changesets) - 1)]
            self._vars['mdate'] = int(last_changeset.date()[0])
        if 'mdate' in self._vars:
            self._vars['mdatetime'] = \
                datetime.utcfromtimestamp(self._vars['mdate'])
        if 'author' not in self._vars:
            try:
                self._vars['author'] = str(first_changeset.user())
            except:
                del self._vars['author']
            else:
                if self._vars['author'] == '':
                    try:
                        self._vars['author'] = str(self._filectx.user())
                    except:
                        del self._vars['author']

    def _set_title(self, title):
        if self._title is None:
            title = title.strip()
            if title != '':
                self._title = title

    @cached_property
    def _parsed_author(self):
        if 'author' not in self._vars:
            return {}
        rv = re_author.match(self._vars['author'])
        if rv is None:
            return {}
        return rv.groupdict()

    @cached_property
    def author_name(self):
        return self._parsed_author.get('name', '')

    @cached_property
    def author_email(self):
        return self._parsed_author.get('email', '')

    @cached_property
    def path(self):
        return self._filectx.path()

    @cached_property
    def slug(self):
        match = re.match(r'%s/(.+)\.rst' % self._content_dir,
            self._filectx.path())
        if match is not None:
            return match.group(1)

    @cached_property
    def title(self):
        # workaround to load the title from rst
        self.abstract_html
        if self._title is not None:
            return self._title
        return self._vars.get('title', u'')

    @cached_property
    def tags(self):
        return self._vars.get('tags', [])

    @cached_property
    def abstract(self):
        return re_read_more.split(self._filecontent)[0].decode('utf-8')

    @cached_property
    def abstract_html(self):
        parts = rst2html(self.abstract)
        self._set_title(parts['title'])
        return parts['fragment']

    @cached_property
    def full(self):
        return self._filecontent.decode('utf-8')

    @cached_property
    def full_html(self):
        parts = rst2html(self.full)
        self._set_title(parts['title'])
        return parts['fragment']

    @cached_property
    def read_more(self):
        return len(re_read_more.split(self._filecontent)) > 1

    def get(self, key, default=None):
        return self._vars.get(key, default)

    def __getattr__(self, attr):
        return self.get(attr)

    def __str__(self):
        return self._filecontent

    def __repr__(self):
        return '<Metadata %r>' % self.slug
