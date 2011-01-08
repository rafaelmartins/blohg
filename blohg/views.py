# -*- coding: utf-8 -*-
"""
    blohg.views
    ~~~~~~~~~~~
    
    A generic Flask Module with all the views.
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import math

from flask import Module, abort, current_app, make_response, redirect, \
    render_template, request, url_for
from werkzeug.contrib.atom import AtomFeed, FeedEntry
from blohg.filters import rst2html, tag_name

views = Module(__name__)


@views.route('/atom/')
@views.route('/atom/<tag>/')
@views.route('/rss/')  # dumb redirect to keep the compatibility
@views.route('/rss/<tag>/')  # dumb redirect to keep the compatibility
def feed(tag=None):
    """General purpose atom feed."""
    
    if tag is not None:
        posts = current_app.hg.get_by_tag(tag)
    else:
        posts = current_app.hg.get_all(True)
    feed = AtomFeed(
        title = current_app.config['TITLE'],
        subtitle = current_app.config['TAGLINE'],
        url = url_for('views.home'),
        feed_url = url_for('views.feed', tag=tag),
        author = current_app.config['AUTHOR'],
        generator = ('blohg', None, None)
    )
    for post in posts[:current_app.config['POSTS_PER_PAGE']]:
        feed.add(
            FeedEntry(
                title = post.title,
                content = post.full_html,
                summary = post.abstract_html,
                url = url_for('views.content', slug=post.slug),
                author = current_app.config['AUTHOR'],
                published = post.datetime,
                updated = post.datetime,
            )
        )
    response = make_response(str(feed))
    response.headers['Content-Type'] = 'application/atom+xml; charset=utf-8'
    return response


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
    print current_app.hg.revision_id
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
        'list_posts.html',
        title = u'Posts',
        posts = current_app.hg.get_all(True),
    )


@views.route('/tag/<tag>/')
def tag(tag):
    """Page that lists the abstract of all available posts for the given
    tag.
    """
    
    if tag not in current_app.hg.tags:
        abort(404)
    posts = current_app.hg.get_by_tag(tag)
    return render_template(
        '_posts.html',
        title = u'Tag: %s' % tag_name(tag),
        tag_title = tag,
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

