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
from werkzeug import cached_property

re_metadata = re.compile(r'\.\. +([a-z]*): (.*)')
re_read_more = re.compile(r'\.\. +read_more')


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
        
        # refreshing :)
        if refresh:
            
            # Deleting the app.hg element. Not sure if it's worth :)
            if hasattr(app, 'hg'):
                del app.hg
            
            revision_id = None
            if not app.debug:
                revision_id = 'tip'
            app.hg = MercurialContent(repo, repo[revision_id])


class MercurialContent(object):
    """Object that represents a blohg Mercurial repository."""
    
    def __init__(self, repo, revision):
        """Class constructor"""
        
        self.repo = repo
        self.revision = revision
    
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
            metadata.append(Metadata(self.repo, self.revision[my_filename]))
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
            match = re.match(r'^txt/%s/(.+)\.rst$' % locale, filename)
            if match is not None:
                filenames.append(match.group(1))
        return filenames
    
    def __repr__(self):
        return '<Mercurial %r>' % self.repo.root
    

class Metadata(object):
    """Static page/Post metadata object."""
    
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
        for i in re_metadata.finditer(self._filecontent):
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
    
    @cached_property
    def name(self):
        match = re.match(r'txt/[^/]+/(.+)\.rst', self._filectx.path())
        if match is not None:
            return match.group(1)
    
    @cached_property
    def abstract(self):
        return re_read_more.split(self._filecontent)[0].decode('utf-8')
    
    @cached_property
    def full(self):
        return self._filecontent.decode('utf-8')
    
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
        return '<Metadata %r>' % self.name
