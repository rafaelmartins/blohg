# -*- coding: utf-8 -*-
"""
    blohg.views
    ~~~~~~~~~~~

    A generic Flask Module with all the views.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import math

from flask import Blueprint, abort, current_app, make_response, \
     render_template, url_for, redirect
from jinja2 import TemplateNotFound
from werkzeug.contrib.atom import AtomFeed, FeedEntry
from werkzeug.exceptions import NotFound

views = Blueprint('views', __name__)


# this is like a stack. I want 'atom' to be used by url_for, then it should be
# in the latest decorators
@views.route('/rss/')  # dumb redirect to keep the compatibility
@views.route('/rss/<path:tag>/')  # dumb redirect to keep the compatibility
@views.route('/atom/')
@views.route('/atom/<path:tag>/')
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
    feed = AtomFeed(title=title, subtitle=current_app.config['TAGLINE'],
                    url=url_for('views.home', _external=True),
                    id=url_for('views.atom', tag=tag),
                    feed_url=url_for('views.atom', tag=tag, _external=True),
                    author=current_app.config['AUTHOR'],
                    generator=('blohg', None, None))
    for post in posts[:int(current_app.config['POSTS_PER_PAGE'])]:
        feed.add(FeedEntry(title=post.title, content=post.full_raw_html,
                           summary=post.abstract_raw_html,
                           id=url_for('views.content', slug=post.slug),
                           url=url_for('views.content', slug=post.slug,
                                       _external=True),
                           author=dict(name=post.author_name,
                                       email=post.author_email),
                           published=post.datetime, updated=post.datetime))
    return feed


@views.route('/<path:slug>/')
def content(slug):
    """Posts and static pages."""
    page = current_app.hg.get(slug)
    if page is None:
        url = "/%s/" % slug
        if url in current_app.hg.aliases:
            code, slug = current_app.hg.aliases[url]
            return redirect(url_for('views.content', slug=slug), code=code)
        abort(404)
    title = page.title
    if slug.startswith('post'):
        title = u'Post: %s' % page.title
    return render_template('_posts.html', title=title, posts=[page],
                           full_content=True, meta=page)


@views.route('/')
@views.route('/page/<int:page>/')
def home(page=None):
    """Page with the abstract of the posts. Part of the pagination."""
    if page is None:
        try:
            return content('index')
        except NotFound:
            page = 1
    current = int(page)
    pages = current_app.hg.get_all(True)
    ppp = int(current_app.config['POSTS_PER_PAGE'])
    num_pages = int(math.ceil(float(len(pages)) / ppp))
    init = int((current - 1) * ppp)
    end = int(current * ppp)
    return render_template('_posts.html', posts=pages[init:end],
                           full_content=False,
                           pagination={'num_pages': num_pages,
                                       'current': page})


@views.route('/posts/')
def posts():
    """An alias to ``/page/1/``. Not adding it as a decorator to the existing
    view to provide another endpoint.
    """
    return home(1)


@views.route('/post/')
def post_list():
    """Page with a simple list of posts (link + creation date)."""
    try:
        return render_template('post_list.html', title=u'Posts',
                               posts=current_app.hg.get_all(True))
    except TemplateNotFound:
        if 'FREEZER_BASE_URL' in current_app.config:  # freezing the blog
            return ""
        abort(404)


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
    return render_template('_posts.html', title=u'Tag: %s' % ' + '.join(tags),
                           tag=tags, posts=posts, full_content=False)


@views.route('/source/')  # just to make robots.txt's url_for happy :)
@views.route('/source/<path:slug>/')
def source(slug=None):
    """View that shows the source code of a given static page/post. Can be
    disabled setting SHOW_RST_SOURCE configuration parameter to ``False``
    """
    if 'FREEZER_BASE_URL' in current_app.config and slug is None:  # freezing
        return ''
    if not current_app.config['SHOW_RST_SOURCE'] or slug is None:
        abort(404)
    source = current_app.hg.get(slug)
    if source is None:
        abort(404)
    response = make_response(source.full)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response


@views.route('/robots.txt')
def robots():
    """View that generates a robots.txt file for ``/source/``  path, to avoid
    source files to be indexed by search engines. Can be disabled setting
    ROBOTS_TXT configuration parameter to ``False``
    """
    if not current_app.config['ROBOTS_TXT']:
        abort(404)
    response = make_response(render_template('robots.txt'))
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response
