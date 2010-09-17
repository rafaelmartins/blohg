# -*- coding: utf-8 -*-

import re
import time
from mercurial import hg, ui

class MercurialContent(object):
    
    def __init__(self, repo_path, locale, working_dir=False):
        self.repo_path = repo_path
        self._ui = ui.ui()
        self._repo = hg.repository(self._ui, repo_path)
        self.re_rst_files = re.compile(r'txt/%s/(.+)\.rst' % locale)
        self.revision_id = None
        if working_dir != True:
            self.revision_id = 'tip'
        self.revision = self._repo[self.revision_id]
        self.filenames = list(self.revision)
        self.tags = []
        for file in self.get_all():
            tags = file['tags']
            if tags is not None:
                for tag in tags:
                    if tag not in self.tags:
                        self.tags.append(tag)
        self.tags.sort()
    
    def _metadata_from_filenames(self, filenames):
        metadata = []
        for filename in filenames:
            metadata.append(Metadata(self._repo, self.revision[filename]))
        return sorted(metadata, self._compare_by_date)
    
    def _compare_by_date(self, a, b):
        return b['date'] - a['date']
    
    def get(self, filename):
        if filename not in self.filenames:
            return None
        metadata = self._metadata_from_filenames([filename])[0]
        content = str(metadata)
        return content
    
    def get_all(self, only_posts=False):
        my_filenames = []
        for filename in self.filenames:
            pieces = self.re_rst_files.match(filename)
            if pieces is not None:
                if only_posts and not pieces.group(1).startswith('post/'):
                    continue
                my_filenames.append(filename)
        return self._metadata_from_filenames(my_filenames)
    
    def get_by_tag(self, tag):
        posts = self.get_all(only_posts=True)
        my_posts = []
        for post in posts:
            tags = post['tags']
            if tags is not None and tag in tags:
                my_posts.append(post)
        return my_posts
    
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
        if len(changesets) > 1:
            last_changeset = self._repo[filelog.linkrev(len(changesets)-1)]
            self._vars['mdate'] = int(last_changeset.date()[0])
        
    def __getitem__(self, key):
        return self.get(key)
    
    def __str__(self):
        return self._filecontent
    
    @property
    def name(self):
        return self._filectx.path()
    
    @property
    def abstract(self, filecontent):
        return self._re_read_more.split(self._filecontent)[0]
    
    def get(self, key, default=None):
        return self._vars.get(key, default)
    
    def __repr__(self):
        return '<Metadata %r>' % self.name

