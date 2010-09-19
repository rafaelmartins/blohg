from flask import Module, current_app, make_response, abort

from blohg.decorators import validate_locale

source = Module(__name__)

@source.route('/<locale>/source/<path:slug>/')
@validate_locale
def page(locale, slug):
    source = current_app.hg.get(locale, slug)
    if source is None:
        abort(404)
    response = make_response(source.full)
    response.headers['Content-Type'] = 'text/plain'
    return response
