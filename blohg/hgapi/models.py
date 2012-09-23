# -*- coding: utf-8 -*-
"""
    blohg.hgapi.models
    ~~~~~~~~~~~~~~~~~~

    Module with the basic classes for the mercurial content handling.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import re
import time

from datetime import datetime
from flask.helpers import locked_cached_property
from jinja2 import Markup
from mercurial import encoding

from blohg.rst import parser
from blohg.utils import parse_date

re_metadata = re.compile(r'\.\. +([a-z]+): *(.+)')
re_read_more = re.compile(r'\.\. +read_more')
re_author = re.compile(r'^(?P<name>[^<]*[^ ])( ?<(?P<email>[^<]*)>)?$')


def hg2u(s):
    """ returns a unicode object representing the mercurial string """
    return encoding.fromlocal(s).decode("utf-8")


class Page(object):
    """Pages are the very basic content element of a blog. They don't have tags
    nor other fancy stuff that belongs to posts."""

    def __init__(self, parent, filectx):
        self._parent = parent
        self._filectx = filectx
        self._filecontent = filectx.data()
        self._vars = {}
        self._title = None

        # get metadata variables from rst source
        for i in re_metadata.finditer(self._filecontent):
            self._vars[i.group(1)] = hg2u(i.group(2).strip())

        # handle aliases
        if 'aliases' in self._vars:
            self._vars['aliases'] = [i.strip() for i in \
                                     self._vars['aliases'].split(',')]

        # get the creation date, from the time of the first changeset with this
        # content or from the 'date' variable.
        filelog = self._filectx.filelog()
        changesets = list(filelog)
        first_changeset = self._parent.repo[filelog.linkrev(0)]
        if 'date' in self._vars:
            self._vars['date'] = parse_date(self._vars['date'])
        else:
            self._vars['date'] = int(first_changeset.date()[0])
            if self._vars['date'] == 0:
                self._vars['date'] = int(time.time())
        self._vars['datetime'] = datetime.utcfromtimestamp(self._vars['date'])

        # get the modification date, from the time of the last changeset with
        # changes for this content, from the creation date, if this content was
        # never changed, or from the 'mdate' variable.
        if 'mdate' in self._vars:
            self._vars['mdate'] = parse_date(self._vars['mdate'])
        if 'mdate' not in self._vars and len(changesets) > 1:
            last_changeset = self._parent.repo[filelog.linkrev(
                len(changesets) - 1)]
            self._vars['mdate'] = int(last_changeset.date()[0])
        if 'mdate' in self._vars:
            self._vars['mdatetime'] = \
                datetime.utcfromtimestamp(self._vars['mdate'])

        # get the author name/email from the 'author' variable or from the
        # commiter of this content to the repository.
        if 'author' not in self._vars:
            try:
                self._vars['author'] = hg2u(first_changeset.user())
            except:
                del self._vars['author']
            else:
                if self._vars['author'] == u'':
                    try:
                        self._vars['author'] = hg2u(self._filectx.user())
                    except:
                        del self._vars['author']

    @locked_cached_property
    def parsed_source(self):
        return parser(self.full)

    @locked_cached_property
    def parsed_abstract(self):
        if not self.read_more:
            return self.parsed_source
        return parser(self.abstract)

    @locked_cached_property
    def parsed_author(self):
        if 'author' not in self._vars:
            return {}
        rv = re_author.match(self._vars['author'])
        if rv is None:
            return {'name': self._vars['author']}
        return rv.groupdict()

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
        if 'name' in self.parsed_author:
            return self.parsed_author['name']

    @locked_cached_property
    def author_email(self):
        if 'email' in self.parsed_author:
            return self.parsed_author['email']

    @locked_cached_property
    def path(self):
        return self._filectx.path()

    @locked_cached_property
    def slug(self):
        rv = re.match(r'^' + self._parent.content_dir + r'[\\/](.+)' +
                      '\\' + self._parent.post_ext + '$',
                      self._filectx.path())
        if rv is not None:
            return rv.group(1)

    @locked_cached_property
    def aliases(self):
        return self._vars.get('aliases', [])

    @locked_cached_property
    def abstract(self):
        return hg2u(re_read_more.split(self._filecontent)[0])

    @locked_cached_property
    def abstract_html(self):
        return Markup(self.parsed_abstract['fragment'])

    @locked_cached_property
    def abstract_raw_html(self):
        return self.parsed_abstract['fragment']

    @locked_cached_property
    def full(self):
        return hg2u(self._filecontent)

    @locked_cached_property
    def full_html(self):
        return Markup(self.parsed_source['fragment'])

    @locked_cached_property
    def full_raw_html(self):
        return self.parsed_source['fragment']

    @locked_cached_property
    def read_more(self):
        return len(re_read_more.split(self._filecontent)) > 1

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

    def __init__(self, parent, filectx):
        Page.__init__(self, parent, filectx)

        # handle tags
        if 'tags' in self._vars:
            self._vars['tags'] = [i.strip() for i in \
                                  self._vars['tags'].split(',')]

    @locked_cached_property
    def tags(self):
        return self._vars.get('tags', [])
