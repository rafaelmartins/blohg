# -*- coding: utf-8 -*-
"""
    blohg.hgapi
    ~~~~~~~~~~~

    Package with Mercurial-related stuff needed by blohg to load posts
    and static pages.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import re
import time
import yaml

from jinja2.loaders import ChoiceLoader
from mercurial import hg, ui as _ui
from blohg.hgapi.models import Page, Post
from blohg.hgapi.repo import Repository, STATE_STABLE, STATE_VARIABLE
from blohg.hgapi.static import MercurialStaticFile
from blohg.hgapi.templates import MercurialLoader


def setup_mercurial(app, ui=None):
    """This function adds a :class:`Hg` instance to an application object, as a
    ``hg`` attribute, and reloads it as needed.

    :param app: the application object, must have a 'REPO_PATH' configuration
                parameter.
    :param hgui: a Mercurial ui object.
    """

    # create an ui object and attach the Hg object to app
    app.hg = Hg(app, ui)

    # setup our jinja2 custom loader and static file handlers
    old_loader = app.jinja_loader
    app.jinja_loader = ChoiceLoader([MercurialLoader(), old_loader])
    app.add_url_rule(app.static_url_path + '/<path:filename>',
                     endpoint='static',
                     view_func=MercurialStaticFile('STATIC_DIR'))
    app.add_url_rule('/attachments/<path:filename>', endpoint='attachments',
                     view_func=MercurialStaticFile('ATTACHMENT_DIR'))

    @app.before_request
    def before_request():
        app.hg.reload()


class Hg(object):
    """Main class of the Mercurial layer."""

    def __init__(self, app, ui=None):
        self.app = app
        self.repo = Repository(self.app.config.get('REPO_PATH', '.'), ui)

        # the state comes from the Flask configuration, but NOT from the yaml
        # file in the repository.
        state_name = self.app.config.get('STATE', 'stable').lower()
        if state_name == 'stable':
            self.state_id = STATE_STABLE
        elif state_name == 'variable':
            self.state_id = STATE_VARIABLE
        else:
            raise RuntimeError('Invalid state: %s' % state_name)
        self.state = self.repo.get_repostate(self.state_id)
        self._load_config()

        self.content_dir = None
        self.post_ext = None
        self.rst_header_level = None
        self.pages = []
        self.posts = []
        self.tags = set()
        self.aliases = {}
        self.reload()

    def _parse_aliases(self, post_or_page):
        for alias in post_or_page.aliases:
            code = 302
            alias = alias.encode('utf-8')
            if alias[:4] in ('301:', '302:'):
                code = int(alias[:3])
                alias = alias[4:]
            self.aliases[alias.encode('utf-8')] = (code, post_or_page.slug)

    def _load_config(self):
        config = yaml.load(self.state.get('config.yaml'))

        # state can't be defined by the config.yaml file. filter it.
        if 'STATE' in config:
            del config['STATE']

        # monkey-patch configs when running from built-in server
        if self.app.config.get('RUNNING_FROM_CLI', False):
            if 'GOOGLE_ANALYTICS' in config:
                del config['GOOGLE_ANALYTICS']
            config['DISQUS_DEVELOPER'] = True

        self.app.config.update(config)

    def reload(self):
        """Method to reload stuff from the Mercurial repository. It is able to
        reload as needed, to save resources.
        """

        if not self.state.needs_reload():
            return

        self.state = self.repo.get_repostate(self.state_id)
        self._load_config()

        # build a regular expression for search posts/pages.
        self.content_dir = self.app.config.get('CONTENT_DIR', 'content')
        self.post_ext = self.app.config.get('POST_EXT', '.rst')
        re_content = re.compile(r'^' + self.content_dir + \
                                r'[\\/](post)?.+' + '\\' + self.post_ext + '$')

        self.rst_header_level = self.app.config['RST_HEADER_LEVEL']

        # get all the content
        self.pages = []
        self.posts = []
        self.tags = set()
        self.aliases = {}
        now = int(time.time())
        for fname in self.state.files:
            rv = re_content.match(fname)
            if rv is not None:
                if rv.group(1) is None:  # page
                    page = Page(self.app.hg.state._repo, self.state.get_fctx(fname),
                                self.content_dir, self.post_ext,
                                self.rst_header_level)
                    if not self.app.debug and page.date > now:
                        continue
                    self._parse_aliases(page)
                    self.pages.append(page)
                else:  # post
                    post = Post(self.app.hg.state._repo, self.state.get_fctx(fname),
                                self.content_dir, self.post_ext,
                                self.rst_header_level)
                    if not self.app.debug and post.date > now:
                        continue
                    self._parse_aliases(post)
                    self.posts.append(post)
                    self.tags = self.tags.union(set(post.tags))

        # sort tags by "name" and convert them back to a list
        self.tags = sorted(self.tags)

        # sort posts reverse by date. sort pages is useless :P
        self.posts = sorted(self.posts, lambda a, b: b.date - a.date)

    def get(self, slug):
        """Method that returns a :class:`Page` or a :class:`Post` object for
        a given slug.

        :param slug: the slug string.
        :return: a :class:`Page` or a :class:`Post`
        """
        for entry in self.posts + self.pages:
            if entry.slug == slug:
                return entry

    def get_all(self, only_posts=False):
        """Method that returns a list of :class:`Page` or :class:`Post`
        objects for all the available files.

        :param only_posts: a boolean that makes the method returns only
                           the available posts for the given locale, not
                           the static pages.
        :return: a list of :class:`Page` or :class:`Post` objects.
        """
        if only_posts:
            return self.posts
        return self.posts + self.pages

    def get_by_tag(self, tag):
        """Method that returns a list of :class:`Post` objects for a
        given list of tag identifier strings.

        :param tag: a list of tag identifier strings.
        :return: a list of :class:`Post` objects.
        """
        posts = []
        for post in self.posts:
            found = True
            for _tag in tag:
                if _tag not in post.tags:
                    found = False
            if found:
                posts.append(post)
        return posts

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.repo.root)
