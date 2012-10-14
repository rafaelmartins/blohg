# -*- coding: utf-8 -*-
"""
    blohg.models
    ~~~~~~~~~~~~

    Module with the basic classes for the mercurial content handling.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
import re
import time
import yaml

from datetime import datetime
from flask.helpers import locked_cached_property
from jinja2 import Markup

from blohg.hg import HgRepository, REVISION_DEFAULT, REVISION_WORKING_DIR
from blohg.rst import parser
from blohg.utils import parse_date

re_metadata = re.compile(r'\.\. +([a-z]+): *(.+)')
re_read_more = re.compile(r'\.\. +read_more')
re_author = re.compile(r'^(?P<name>[^<]*[^ ])( ?<(?P<email>[^<]*)>)?$')


class Page(object):
    """Pages are the very basic content element of a blog. They don't have tags
    nor other fancy stuff that belongs to posts."""

    def __init__(self, filectx, content_dir, post_ext, rst_header_level):
        self._filectx = filectx
        self._content_dir = content_dir
        self._post_ext = post_ext
        self._rst_header_level = rst_header_level
        self._vars = {}
        self._title = None

        # get metadata variables from rst source.
        for i in re_metadata.finditer(self._filectx.content):
            self._vars[i.group(1).strip()] = i.group(2).strip()

    @locked_cached_property
    def parsed_source(self):
        return parser(self.full, self._rst_header_level)

    @locked_cached_property
    def parsed_abstract(self):
        if not self.read_more:
            return self.parsed_source
        return parser(self.abstract, self._rst_header_level)

    @locked_cached_property
    def author(self):
        # get the author name/email from the 'author' variable or from the
        # commiter of this content to the repository.
        author_dict = {'name': None, 'email': None}
        author = self._vars.get('author', self._filectx.author)
        if not author:
            return author_dict
        rv = re_author.match(author)
        if rv is None:
            author_dict['name'] = author
            return author_dict
        author_dict.update(rv.groupdict())
        return author_dict

    @locked_cached_property
    def title(self):
        return self._vars.get('title', self.parsed_source['title'])

    @locked_cached_property
    def description(self):
        return self._vars.get('description',
                              self.parsed_source['first_paragraph_as_text'])

    @locked_cached_property
    def images(self):
        return self.parsed_source.get('images', [])

    @locked_cached_property
    def flash_videos(self):
        return self.parsed_source.get('flash_videos', [])

    @locked_cached_property
    def author_name(self):
        if 'name' in self.author:
            return self.author['name']

    @locked_cached_property
    def author_email(self):
        if 'email' in self.author:
            return self.author['email']

    @locked_cached_property
    def path(self):
        return self._filectx.path

    @locked_cached_property
    def slug(self):
        rv = re.match(r'^' + self._content_dir + r'[\\/](.+)' +
                      '\\' + self._post_ext + '$',
                      self._filectx.path)
        if rv is not None:
            return rv.group(1)

    @locked_cached_property
    def date(self):
        # get the creation date, from the time of the first changeset with this
        # content or from the 'date' variable.
        if 'date' in self._vars:
            return parse_date(self._vars['date'])
        return parse_date(self._filectx.date)

    @locked_cached_property
    def datetime(self):
        return datetime.utcfromtimestamp(self.date)

    @locked_cached_property
    def mdate(self):
        # get the modification date, from the time of the last changeset with
        # changes for this content, from the creation date, if this content was
        # never changed, or from the 'mdate' variable.
        if 'mdate' in self._vars:
            return parse_date(self._vars['mdate'])
        mdate = self._filectx.mdate
        if mdate is not None:
            return parse_date(mdate)

    @locked_cached_property
    def mdatetime(self):
        if self.mdate is not None:
            return datetime.utcfromtimestamp(self.mdate)

    @locked_cached_property
    def aliases(self):
        # handle aliases
        if 'aliases' not in self._vars:
            return []
        return [i.strip() for i in self._vars['aliases'].split(',')]

    @locked_cached_property
    def abstract(self):
        return re_read_more.split(self._filectx.content)[0]

    @locked_cached_property
    def abstract_html(self):
        return Markup(self.parsed_abstract['fragment'])

    @locked_cached_property
    def abstract_raw_html(self):
        return self.parsed_abstract['fragment']

    @locked_cached_property
    def full(self):
        return self._filectx.content

    @locked_cached_property
    def full_html(self):
        return Markup(self.parsed_source['fragment'])

    @locked_cached_property
    def full_raw_html(self):
        return self.parsed_source['fragment']

    @locked_cached_property
    def read_more(self):
        return len(re_read_more.split(self._filectx.content)) > 1

    def get(self, key, default=None):
        return self._vars.get(key, default)

    def __getattr__(self, attr):
        return self.get(attr)

    def __str__(self):
        return self.full

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.slug)


class Post(Page):
    """Posts are like pages, but with tags support."""

    @locked_cached_property
    def tags(self):
        # handle tags
        if 'tags' not in self._vars:
            return []
        return [i.strip() for i in self._vars['tags'].split(',')]


class Hg(object):
    """Main class of the Mercurial layer."""

    def __init__(self, app, ui=None):
        self.app = app
        self.repo = HgRepository(self.app.config.get('REPO_PATH', '.'), ui)
        self.ctx = None
        self.content_dir = None
        self.post_ext = None
        self.rst_header_level = None
        self.pages = []
        self.posts = []
        self.tags = set()
        self.aliases = {}

    def _parse_aliases(self, post_or_page):
        for alias in post_or_page.aliases:
            code = 302
            alias = alias.encode('utf-8')
            if alias[:4] in ('301:', '302:'):
                code = int(alias[:3])
                alias = alias[4:]
            self.aliases[alias.encode('utf-8')] = (code, post_or_page.slug)

    def _load_config(self):
        config = yaml.load(self.ctx.get_filectx('config.yaml').content)

        # revision can't be defined by the config.yaml file. filter it.
        if 'REVISION' in config:
            del config['REVISION']

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

        # the state comes from the Flask configuration, but NOT from the yaml
        # file in the repository.
        revision_name = self.app.config['REVISION'].lower()
        if revision_name == 'default':
            self.revision_id = REVISION_DEFAULT
        elif revision_name == 'working_dir':
            self.revision_id = REVISION_WORKING_DIR
        else:
            raise RuntimeError('Invalid revision: %s' % revision_name)

        # if called from the initrepo script command the repository will not
        # exists, then it shouldn't be loaded
        if not os.path.exists(self.repo.path):
            return

        if self.ctx is not None and not self.ctx.needs_reload():
            return

        self.ctx = self.repo.get_changectx(self.revision_id)
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
        for fname in self.ctx.files:
            rv = re_content.match(fname)
            if rv is not None:
                if rv.group(1) is None:  # page
                    page = Page(self.ctx.get_filectx(fname),
                                self.content_dir, self.post_ext,
                                self.rst_header_level)
                    if not self.app.debug and page.date > now:
                        continue
                    self._parse_aliases(page)
                    self.pages.append(page)
                else:  # post
                    post = Post(self.ctx.get_filectx(fname),
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
        return '<%s %r>' % (self.__class__.__name__, self.repo.path)
