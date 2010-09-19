# -*- coding: utf-8 -*-

import re
import time

from datetime import datetime
from mercurial import hg, ui

def setup_mercurial(app):
    app.hg = MercurialContent(app)

class MercurialContent(object):
    
    def __init__(self, app):
        self.repo_path = app.config.get('REPO_PATH', '.')
        self._ui = ui.ui()
        self._repo = hg.repository(self._ui, self.repo_path)
        self.revision_id = None
        if not app.debug:
            self.revision_id = 'tip'
        self.revision = self._repo[self.revision_id]
    
    def _metadata_from_filenames(self, locale, filenames):
        metadata = []
        for filename in filenames:
            my_filename = 'txt/%s/%s.rst' % (locale, filename)
            metadata.append(Metadata(self._repo, self.revision[my_filename]))
        return sorted(metadata, self._compare_by_date)
    
    def _compare_by_date(self, a, b):
        return b['date'] - a['date']
    
    def get(self, locale, filename):
        if filename not in self.get_filenames(locale):
            return None
        return self._metadata_from_filenames(locale, [filename])[0]
    
    def get_all(self, locale, only_posts=False):
        my_filenames = []
        for filename in self.get_filenames(locale):
            if only_posts and not filename.startswith('post/'):
                continue
            my_filenames.append(filename)
        return self._metadata_from_filenames(locale, my_filenames)
    
    def get_by_tag(self, locale, tag):
        posts = self.get_all(locale, only_posts=True)
        my_posts = []
        for post in posts:
            tags = post['tags']
            if tags is not None and tag in tags:
                my_posts.append(post)
        return my_posts
    
    def get_tags(self, locale):
        my_tags = []
        for file in self.get_all(locale):
            tags = file['tags']
            if tags is not None:
                for tag in tags:
                    if tag not in my_tags:
                        my_tags.append(tag)
        my_tags.sort()
        return my_tags
    
    def get_filenames(self, locale):
        filenames = []
        for filename in self.revision:
            match = re.match(r'txt/%s/(.+)\.rst' % locale, filename)
            if match is not None:
                filenames.append(match.group(1))
        return filenames
    
    def __repr__(self):
        return '<Mercurial %r>' % self.repo_path
    

class Metadata(object):
    
    _re_metadata = re.compile(r'\.\. +([a-z]*): (.*)')
    _re_read_more = re.compile(r'\.\. +read_more')
    
    def __init__(self, repo, filectx):
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
        first_changeset = self._repo[filelog.linkrev(0)]
        self._vars['date'] = int(first_changeset.date()[0])
        if self._vars['date'] == 0:
            self._vars['date'] = int(time.time())
        self._vars['datetime'] = datetime.utcfromtimestamp(self._vars['date'])
        if len(changesets) > 1:
            last_changeset = self._repo[filelog.linkrev(len(changesets)-1)]
            self._vars['mdate'] = int(last_changeset.date()[0])
            self._vars['mdatetime'] = datetime.utcfromtimestamp(self._vars['mdate'])
    
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
    
    @property
    def locale(self):
        match = re.match(r'txt/%s/(.+)\.rst' % locale, self._filectx.path())
        if match is not None:
            return match.group(1)
        return None
    
    def get(self, key, default=None):
        return self._vars.get(key, default)
    
    def __getitem__(self, key):
        return self.get(key)
    
    def __str__(self):
        return self._filecontent
    
    def __repr__(self):
        return '<Metadata %r>' % self.name

