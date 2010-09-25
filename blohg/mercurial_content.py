# -*- coding: utf-8 -*-

"""
    blohg.mercurial_content
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    Module with all the Mercurial-related stuff needed by blohg.
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import re, time
from datetime import datetime
from mercurial import hg, ui


def setup_mercurial(app):
    """This function adds a :class:`MercurialContent` instance to an
    application object, as a ``hg`` attribute.
    
    :param app: the application object.
    """
    
    app.hg = MercurialContent(app)


class MercurialContent(object):
    """Object that represents a blohg Mercurial repository."""
    
    def __init__(self, app):
        """Class constructor"""
        
        self.repo_path = app.config.get('REPO_PATH', '.')
        self._ui = ui.ui()
        self._repo = hg.repository(self._ui, self.repo_path)
        self.revision_id = None
        if not app.debug:
            self.revision_id = 'tip'
        self.revision = self._repo[self.revision_id]
    
    def _metadata_from_filenames(self, locale, filenames):
        """Method to convert a list of filenames on a list of
        :class:`Metadata` objects, sorted by creation date.
        
        :param locale: the current locale string.
        :param filenames: the list of filenames.
        :return: a list of :class:`Metadata` objects.
        """
        
        metadata = []
        for filename in filenames:
            my_filename = 'txt/%s/%s.rst' % (locale, filename)
            metadata.append(Metadata(self._repo, self.revision[my_filename]))
        return sorted(metadata, self._compare_by_date)
    
    def _compare_by_date(self, a, b):
        """Method that compares 2 :class:`Metadata` objects by creation
        date.
        """
        
        return b.date - a.date
    
    def get(self, locale, filename):
        """Method that returns a :class:`Metadata` object for a given
        filename.
        
        :param locale: the current locale string.
        :param filename: the file name string.
        :return: a :class:`Metadata` object.
        """
        
        if filename not in self.get_filenames(locale):
            return None
        return self._metadata_from_filenames(locale, [filename])[0]
    
    def get_all(self, locale, only_posts=False):
        """Method that returns a list of :class:`Metadata` objects for
        all the available files for the given locale, ordered by creation
        date.
        
        :param locale: the current locale string.
        :param only_posts: a boolean that makes the method returns only
                           the available posts for the given locale, not
                           the static pages.
        :return: a list of :class:`Metadata` objects.
        """
        
        my_filenames = []
        for filename in self.get_filenames(locale):
            if only_posts and not filename.startswith('post/'):
                continue
            my_filenames.append(filename)
        return self._metadata_from_filenames(locale, my_filenames)
    
    def get_by_tag(self, locale, tag):
        """Method that returns a list of :class:`Metadata` objects for a
        given tag identifier.
        
        :param locale: the current locale string.
        :param tag: the tag identifier string.
        :return: a list of :class:`Metadata` objects.
        """
        
        posts = self.get_all(locale, only_posts=True)
        my_posts = []
        for post in posts:
            tags = post.tags
            if tags is not None and tag in tags:
                my_posts.append(post)
        return my_posts
    
    def get_tags(self, locale):
        """Method that returns a list of all the available tag identifiers
        for a given locale.
        
        :param locale: the current locale string.
        :return: a list of tag identifiers strings.
        """
        
        my_tags = []
        for file in self.get_all(locale):
            tags = file.tags
            if tags is not None:
                for tag in tags:
                    if tag not in my_tags:
                        my_tags.append(tag)
        my_tags.sort()
        return my_tags
    
    def get_filenames(self, locale):
        """Method that returns a list of all the available file names
        for a given locale.
        
        :param locale: the current locale string.
        :return: a list of file names strings.
        """
        
        filenames = []
        for filename in self.revision:
            match = re.match(r'txt/%s/(.+)\.rst' % locale, filename)
            if match is not None:
                filenames.append(match.group(1))
        return filenames
    
    def __repr__(self):
        return '<Mercurial %r>' % self.repo_path
    

class Metadata(object):
    """Static page/Post metadata object."""
    
    _re_metadata = re.compile(r'\.\. +([a-z]*): (.*)')
    _re_read_more = re.compile(r'\.\. +read_more')
    
    def __init__(self, repo, filectx):
        """Class constructor.
        
        :param repo: a Mercurial repository object (not
                     :class:`MercurialContent`)
        :param filectx: the Mercurial file context of the file.
        """
        
        self._repo = repo
        self._filectx = filectx
        self._filecontent = filectx.data()
        self._vars = {}
        for i in self._re_metadata.finditer(self._filecontent):
            self._vars[i.group(1)] = i.group(2).decode('utf-8')
        if 'tags' in self._vars:
            self._vars['tags'] = self._vars['tags'].strip().split(',')
        filelog = self._filectx.filelog()
        changesets = list(filelog)
        if 'date' in self._vars:
            try:
                self._vars['date'] = int(self._vars['date'])
            except ValueError:
                del self._vars['date']
        if 'date' not in self._vars:
            first_changeset = self._repo[filelog.linkrev(0)]
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
    
    @property
    def name(self):
        match = re.match(r'txt/[^/]+/(.+)\.rst', self._filectx.path())
        if match is not None:
            return match.group(1)
    
    @property
    def abstract(self):
        return self._re_read_more.split(self._filecontent)[0].decode('utf-8')
    
    @property
    def full(self):
        return self._filecontent.decode('utf-8')
    
    @property
    def read_more(self):
        return len(self._re_read_more.split(self._filecontent)) > 1
    
    def get(self, key, default=None):
        return self._vars.get(key, default)
    
    def __getattr__(self, attr):
        return self.get(attr)
    
    def __str__(self):
        return self._filecontent
    
    def __repr__(self):
        return '<Metadata %r>' % self.name
