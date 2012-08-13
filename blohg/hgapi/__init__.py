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
from mercurial import hg, ui, cmdutil
from blohg.hgapi.models import Page, Post
from blohg.hgapi.static import MercurialStaticFile
from blohg.hgapi.templates import MercurialLoader


def setup_mercurial(app, hgui=None):
    """This function adds a :class:`Hg` instance to an application object, as a
    ``hg`` attribute, and reloads it as needed.

    :param app: the application object, must have a 'REPO_PATH' configuration
                parameter.
    :param hgui: a Mercurial ui object.
    """

    # create an ui object and attach the Hg object to app
    app.hgui = hgui or ui.ui()
    app.hg = Hg(app)

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

    def __init__(self, app, config_file=None):
        self.app = app
        self.config_file = config_file or 'config.yaml'
        self.repo = None
        self.revision = None
        self.revision_id = None
        self.default_branch = None
        self.content_dir = None
        self.post_ext = None
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

    def reload(self):
        """Method to reload stuff from the Mercurial repository. It is able to
        reload as needed, to save resources.
        """
        needed = False

        # a new repo object is always needed, for reloads or vefify the if the
        # current stuff is new enough
        repopath = self.app.config.get('REPO_PATH', '.')
        repopath = cmdutil.findrepo(repopath)

        # if findrepo returns None we don't have a repo (yet).
        if repopath is None:
            return

        repo = hg.repository(self.app.hgui, repopath)
        try:
            default_branch = repo.branchtags()['default']
        except KeyError:
            default_branch = None

        # initialize it if needed
        if self.repo is None or self.revision is None:
            needed = True

        # debug mode wants a reload
        if self.app.debug:
            needed = True

        # if we don't need a refresh yet, let's verify if our current revision
        # is new enough
        if not needed:
            if repo[default_branch].rev() != \
               self.repo[self.default_branch].rev():
                needed = True

        if not needed:
            return

        # check which stuff we want.
        #     None: uncommited stuff.
        #     default: last commited stuff.
        revision_id = None
        if not self.app.debug:
            revision_id = default_branch

        # register our shiny new stuff
        self.repo = repo
        self.revision = repo[revision_id]
        self.revision_id = revision_id
        self.default_branch = default_branch

        # load configs
        if self.config_file not in self.revision.manifest():
            raise RuntimeError('Configuration file not found: %s' % \
                               self.config_file)
        config = self.revision[self.config_file].data()
        self.app.config.update(yaml.load(config))

        # monkey-patch configs for debug
        if self.app.debug:
            if 'GOOGLE_ANALYTICS' in self.app.config:
                del self.app.config['GOOGLE_ANALYTICS']
            self.app.config['DISQUS_DEVELOPER'] = True

        # build a regular expression for search posts/pages.
        self.content_dir = self.app.config.get('CONTENT_DIR', 'content')
        self.post_ext = self.app.config.get('POST_EXT', '.rst')
        re_content = re.compile(r'^' + self.content_dir + \
                                r'[\\/](post)?.+' + '\\' + self.post_ext + '$')

        # get all the content
        self.pages = []
        self.posts = []
        self.tags = set()
        self.aliases = {}
        now = int(time.time())
        for fname in self.revision.manifest():
            rv = re_content.match(fname)
            if rv is not None:
                if rv.group(1) is None:  # page
                    page = Page(self, self.revision[fname])
                    if not self.app.debug and page.date > now:
                        continue
                    self._parse_aliases(page)
                    self.pages.append(page)
                else:  # post
                    post = Post(self, self.revision[fname])
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
