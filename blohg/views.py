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
    render_template, request
from werkzeug.contrib.atom import AtomFeed, FeedEntry
from werkzeug.http import parse_accept_header

from blohg.decorators import validate_locale
from blohg.filters import rst2html, tag_name
from blohg.functions import i18n_url_for

views = Module(__name__)


@views.route('/')
def home():
    """Fake home page. Redirects to the preferred language of the browser
    or to the first language on the ``app.config['LOCALES']`` variable.
    """
    default_locale = current_app.config.get('DEFAULT_LOCALE', None)
    if default_locale is not None:
        return redirect(i18n_url_for('views.pagination', locale=default_locale))
    accept_locales = \
        parse_accept_header(request.environ['HTTP_ACCEPT_LANGUAGE'])
    for locale, q in accept_locales:
        locale = locale.lower()
        if locale in current_app.config['LOCALES']:
            return redirect(i18n_url_for('views.pagination', locale=locale))
    first_locale = current_app.config['LOCALES'].keys()[0]
    return redirect(i18n_url_for('views.pagination', locale=first_locale))


@views.route('/<locale>/atom/')
@views.route('/<locale>/rss/')  # dumb redirect to keep the compatibility
@validate_locale
def feed(locale):
    """General purpose atom feed."""
    
    posts = current_app.hg.get_all(locale, True)
    return _feed(locale, posts, i18n_url_for('views.feed'))


@views.route('/<locale>/atom/<tag>/')
@views.route('/<locale>/rss/<tag>/')  # dumb redirect to keep the compatibility
@validate_locale
def feed_by_tag(locale, tag):
    """Tag-specific atom feed."""
    
    posts = current_app.hg.get_by_tag(locale, tag)
    return _feed(locale, posts, i18n_url_for('views.feed_by_tag'))


def _feed(locale, posts, feed_url):
    """Helper function that generates the atom feed from a list of
    posts and the feed url.
    """
    
    posts = posts[:current_app.config['POSTS_PER_PAGE']]
    feed = AtomFeed(
        title = current_app.i18n_config('TITLE'),
        subtitle = current_app.i18n_config('TAGLINE'),
        url = i18n_url_for('views.pagination'),
        feed_url = feed_url,
        author = current_app.config['AUTHOR'],
        generator = ('blohg', None, None)
    )
    for post in posts:
        feed.add(
            FeedEntry(
                title = post.title,
                content = post.full_html,
                summary = post.abstract_html,
                url = i18n_url_for('views.content', slug=post.name),
                author = current_app.config['AUTHOR'],
                published = post.datetime,
                updated = post.datetime,
            )
        )
    response = make_response(str(feed))
    response.headers['Content-Type'] = 'application/atom+xml; charset=utf-8'
    return response


@views.route('/<locale>/<path:slug>/')
@validate_locale
def content(locale, slug):
    """Posts and static pages."""
    page = current_app.hg.get(locale, slug)
    if page is None:
        abort(404)
    title = page.title
    if slug.startswith('post'):
        title = u'Post: %s' % page.title
    return render_template(
        'posts.html',
        title = title,
        posts = [page],
        full_content = True,
    )


@views.route('/<locale>/', defaults={'page': 1})
@views.route('/<locale>/page/<int:page>/')
@validate_locale
def pagination(locale, page):
    """Page with the abstract of the posts. Part of the pagination."""
    
    current = int(page)
    pages = current_app.hg.get_all(locale, True)
    ppp = int(current_app.config['POSTS_PER_PAGE'])
    num_pages = int(math.ceil(float(len(pages)) / ppp))
    init = int((current - 1) * ppp)
    end = int(current * ppp)
    return render_template(
        'posts.html',
        posts = pages[init:end],
        full_content = False,
        pagination = {
            'num_pages': num_pages,
            'current': page,
        }
    )


@views.route('/<locale>/post/')
@validate_locale
def post_list(locale):
    """Page with a simple list of posts (link + creation date)."""
     
    return render_template(
        'list_posts.html',
        title = u'Posts',
        posts = current_app.hg.get_all(locale, True),
    )


@views.route('/<locale>/tag/<tag>/')
@validate_locale
def tag(locale, tag):
    """Page that lists the abstract of all available posts for the given
    tag.
    """
    
    if tag not in current_app.hg.get_tags(locale):
        abort(404)
    posts = current_app.hg.get_by_tag(locale, tag)
    return render_template(
        'posts.html',
        title = u'Tag: %s' % tag_name(tag),
        tag_title = tag,
        posts = posts,
        full_content = False,
    )


@views.route('/robots.txt')
def robots():
    """The robots.txt view."""
    response = make_response(render_template('robots.txt'))
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response


@views.route('/<locale>/source/<path:slug>/')
@validate_locale
def source(locale, slug):
    """View that shows the source code of a given static page/post."""
    
    source = current_app.hg.get(locale, slug)
    if source is None:
        abort(404)
    response = make_response(source.full)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response

