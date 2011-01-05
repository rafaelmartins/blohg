# -*- coding: utf-8 -*-
"""
    blohg.mercurial_content
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    Module with all the Mercurial-related stuff needed by blohg.
    
    :copyright: (c) 2010-2011 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
import re
import time
import yaml

from datetime import datetime
from mercurial import hg, ui
from werkzeug.utils import cached_property

from blohg.filters import rst2html

re_metadata = re.compile(r'\.\. +([a-z]*): (.*)')
re_read_more = re.compile(r'\.\. +read_more')


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
        
        # refreshing :)
        if refresh:
            
            # Deleting the app.hg element. Not sure if it's worth :)
            if hasattr(app, 'hg'):
                del app.hg
            
            revision_id = None
            if not app.debug:
                revision_id = 'tip'
            app.hg = MercurialContent(repo, revision_id)
            load_config(app)
    
    before_request()


class MercurialContent(object):
    """Object that represents a blohg Mercurial repository."""
    
    content_dir = 'txt'
    file_extension = '.rst'
    config_file = 'config/config.yaml'
    
    def __init__(self, repo, revision_id):
        """Class constructor"""
        
        self.repo = repo
        self.revision = repo[revision_id]
    
    @cached_property
    def _pages(self):
        """Method that returns an ordered list with all the pages/posts
        available, for all available locales
        
        :return: a list of :class:`Metadata` objects.
        """
        
        metadata = []
        for filename in self.revision:
            if filename.startswith(self.content_dir + os.sep) and \
               filename.endswith(self.file_extension):
                metadata.append(Metadata(self.repo, self.revision[filename]))
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
        
        full_path = os.path.join(self.content_dir, locale, \
                                 filename + self.file_extension)
        for page in self._pages:
            if page.path == full_path:
                return page
        return None
    
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
        
        my_dir = os.path.join(self.content_dir, locale)
        my_posts_dir = os.path.join(my_dir, 'post')
        metadata = []
        for page in self._pages:
            if page.path.startswith(my_dir) and not only_posts:
                metadata.append(page)
            if page.path.startswith(my_posts_dir):
                metadata.append(page)
        return metadata
    
    def get_by_tag(self, locale, tag):
        """Method that returns a list of :class:`Metadata` objects for a
        given tag identifier.
        
        :param locale: the current locale string.
        :param tag: the tag identifier string.
        :return: a list of :class:`Metadata` objects.
        """
        
        posts = []
        for post in self.get_all(locale, only_posts=True):
            if tag in post.tags:
                posts.append(post)
        return posts
    
    def get_tags(self, locale):
        """Method that returns a list of all the available tag identifiers
        for a given locale.
        
        :param locale: the current locale string.
        :return: a list of tag identifiers strings.
        """
        
        tags = []
        for post in self.get_all(locale, only_posts=True):
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
        else:
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
    def path(self):
        return self._filectx.path()
    
    @cached_property
    def name(self):
        match = re.match(r'txt/[^/]+/(.+)\.rst', self._filectx.path())
        if match is not None:
            return match.group(1)
    
    @cached_property
    def title(self):
        return self._vars.get('title', u'')
    
    @cached_property
    def tags(self):
        return self._vars.get('tags', [])
    
    @cached_property
    def abstract(self):
        return re_read_more.split(self._filecontent)[0].decode('utf-8')

    @cached_property
    def abstract_html(self):
        return rst2html(self.abstract)
    
    @cached_property
    def full(self):
        return self._filecontent.decode('utf-8')
    
    @cached_property
    def full_html(self):
        return rst2html(self.full)
    
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
