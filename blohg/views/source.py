# -*- coding: utf-8 -*-
"""
    blohg.views.source
    ~~~~~~~~~~~~~~~~~~
    
    View module that displays the reStructuredText sources.
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: BSD, see LICENSE for more details.
"""

from flask import Module, current_app, make_response, abort

from blohg.decorators import validate_locale

source = Module(__name__)


@source.route('/<locale>/source/<path:slug>/')
@validate_locale
def source(locale, slug):
    """View that shows the source code of a given static page/post."""
    
    source = current_app.hg.get(locale, slug)
    if source is None:
        abort(404)
    response = make_response(source.full)
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response
