# -*- coding: utf-8 -*-
"""
    blohg.views
    ~~~~~~~~~~~
    
    A generic Flask Module with all the views.
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import math

from flask import Module, abort, current_app, make_response, render_template, \
     url_for
from werkzeug.contrib.atom import AtomFeed, FeedEntry

views = Module(__name__)


@views.route('/atom/')
@views.route('/atom/<path:tag>/')
@views.route('/rss/')  # dumb redirect to keep the compatibility
@views.route('/rss/<path:tag>/')  # dumb redirect to keep the compatibility
def atom(tag=None):
    """General purpose atom feed."""
    
    title = current_app.config['TITLE']
    if tag is not None:
        tags = tag.split('/')
        for _tag in tags:    
            if _tag not in current_app.hg.tags:
                abort(404)
        title += u' » %s' % ' + '.join(tags)
        posts = current_app.hg.get_by_tag(tags)
    else:
        posts = current_app.hg.get_all(True)
    feed = AtomFeed(
        title = title,
        subtitle = current_app.config['TAGLINE'],
        url = url_for('views.home'),
        feed_url = url_for('views.atom', tag=tag),
        author = current_app.config['AUTHOR'],
        generator = ('blohg', None, None)
    )
    for post in posts[:int(current_app.config['POSTS_PER_PAGE'])]:
        feed.add(
            FeedEntry(
                title = post.title,
                content = post.full_html,
                summary = post.abstract_html,
                id = url_for('views.content', slug=post.slug),
                url = url_for('views.content', slug=post.slug, _external=True),
                author = current_app.config['AUTHOR'],
                published = post.datetime,
                updated = post.datetime,
            )
        )
    return feed


@views.route('/<path:slug>/')
def content(slug):
    """Posts and static pages."""
    page = current_app.hg.get(slug)
    if page is None:
        abort(404)
    title = page.title
    if slug.startswith('post'):
        title = u'Post: %s' % page.title
    return render_template(
        '_posts.html',
        title = title,
        posts = [page],
        full_content = True,
    )


@views.route('/', defaults={'page': 1})
@views.route('/page/<int:page>/')
def home(page):
    """Page with the abstract of the posts. Part of the pagination."""
    current = int(page)
    pages = current_app.hg.get_all(True)
    ppp = int(current_app.config['POSTS_PER_PAGE'])
    num_pages = int(math.ceil(float(len(pages)) / ppp))
    init = int((current - 1) * ppp)
    end = int(current * ppp)
    return render_template(
        '_posts.html',
        posts = pages[init:end],
        full_content = False,
        pagination = {
            'num_pages': num_pages,
            'current': page,
        }
    )


@views.route('/post/')
def post_list():
    """Page with a simple list of posts (link + creation date)."""
     
    return render_template(
        'post_list.html',
        title = u'Posts',
        posts = current_app.hg.get_all(True),
    )


@views.route('/tag/<path:tag>/')
def tag(tag):
    """Page that lists the abstract of all available posts for the given
    tag.
    """
    
    tags = tag.split('/')
    for _tag in tags:
        if _tag not in current_app.hg.tags:
            abort(404)
    posts = current_app.hg.get_by_tag(tags)
    return render_template(
        '_posts.html',
        title = u'Tag: %s' % ' + '.join(tags),
        tag = tags,
        posts = posts,
        full_content = False,
    )


@views.route('/source/<path:slug>/')
def source(slug):
    """View that shows the source code of a given static page/post."""
    
    source = current_app.hg.get(slug)
    if source is None:
        abort(404)
    response = make_response(source.full)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response

