# -*- coding: utf-8 -*-
"""
    blohg.views.pages
    ~~~~~~~~~~~~~~~~~
    
    View module that deals with the "static" pages generation.
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from flask import Module, current_app, request, abort, redirect, \
    render_template
from werkzeug.http import parse_accept_header

from blohg.decorators import validate_locale

pages = Module(__name__)


@pages.route('/<locale>/<path:slug>/')
@validate_locale
def page(locale, slug):
    """Static pages."""
    page = current_app.hg.get(locale, slug)
    if page is None:
        abort(404)
    return render_template(
        'posts.html',
        title = page.title,
        posts = [page],
        full_content = True,
    )


@pages.route('/')
def home():
    """Fake home page. Redirects to the preferred language of the browser
    or to the first language on the ``app.config['LOCALES']`` variable.
    """
    default_locale = current_app.config.get('DEFAULT_LOCALE', None)
    if default_locale is not None:
        return redirect(request.script_root + '/' + default_locale + '/') 
    accept_locales = \
        parse_accept_header(request.environ['HTTP_ACCEPT_LANGUAGE'])
    for locale, q in accept_locales:
        locale = locale.lower()
        if locale in current_app.config['LOCALES']:
            return redirect(request.script_root + '/' + locale + '/')
    return redirect(request.script_root + '/' + \
        current_app.config['LOCALES'].keys()[0] + '/')
