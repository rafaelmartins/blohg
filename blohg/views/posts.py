# -*- coding: utf-8 -*-
"""
    blohg.views.posts
    ~~~~~~~~~~~~~~~~~
    
    View module that deals with the blog posts generation.
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: BSD, see LICENSE for more details.
"""

import math

from flask import Module, current_app, abort
from flaskext.themes import render_theme_template

from blohg.decorators import validate_locale
from blohg.filters import tag_name

posts = Module(__name__)


@posts.route('/<locale>/')
@validate_locale
def home(locale):
    """Home page of the given locale, lists the abstract of the last
    available posts.
    """
    
    return page(locale, 1)


@posts.route('/<locale>/page/<int:page>/')
@validate_locale
def page(locale, page):
    """Page with the abstract of the posts. Part of the pagination."""
    
    posts, num_pages = _pagination(
        current_app.hg.get_all(locale, True), page
    )
    return render_theme_template(
        current_app.config['THEME'],
        'posts.html',
        posts = posts,
        full_content = False,
        pagination = {
            'num_pages': num_pages,
            'current': page,
        }
    )


@posts.route('/<locale>/post/<path:slug>/')
@validate_locale
def post(locale, slug):
    """Post page. Shows the full content of a post and the comments, if
    enabled (uses Disqus).
    """
    
    slug = 'post/' + slug
    post = current_app.hg.get(locale, slug)
    if post is None:
        abort(404)
    return render_theme_template(
        current_app.config['THEME'],
        'posts.html',
        title = u'Post: %s' % post.title,
        posts = [post],
        full_content = True,
    )


@posts.route('/<locale>/post/')
@validate_locale
def post_list(locale):
    """Page with a simple list of posts (link + creation date)."""
     
    return render_theme_template(
        current_app.config['THEME'],
        'list_posts.html',
        title = u'Posts',
        posts = current_app.hg.get_all(locale, True),
    )


@posts.route('/<locale>/tag/<tag>/')
@validate_locale
def tag(locale, tag):
    """Page that lists the abstract of all available posts for the given
    tag.
    """
    
    if tag not in current_app.hg.get_tags(locale):
        abort(404)
    posts = current_app.hg.get_by_tag(locale, tag)
    return render_theme_template(
        current_app.config['THEME'],
        'posts.html',
        title = u'Tag: %s' % tag_name(tag),
        tag_title = tag,
        posts = posts,
        full_content = False,
    )


def _pagination(pages, current):
    """Helper function for the pagination of posts."""
    
    current = int(current)
    ppp = int(current_app.config['POSTS_PER_PAGE'])
    num_pages = int(math.ceil(float(len(pages)) / ppp))
    init = int((current - 1) * ppp)
    end = int(current * ppp)
    return pages[init:end], num_pages
