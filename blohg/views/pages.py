from flask import Module, current_app, request, abort, redirect
from flaskext.themes import render_theme_template
from werkzeug import parse_accept_header

from blohg.decorators import validate_locale

pages = Module(__name__)

@pages.route('/<locale>/<path:slug>/')
@validate_locale
def page(locale, slug):
    page = current_app.hg.get(locale, slug)
    if page is None:
        abort(404)
    return render_theme_template(
        current_app.config['THEME'],
        'posts.html',
        posts = [page],
        full_content = True,
    )

@pages.route('/')
def home():
    accept_locales = parse_accept_header(request.environ['HTTP_ACCEPT_LANGUAGE'])
    for locale, q in accept_locales:
        locale = locale.lower()
        if locale in current_app.config['LOCALES']:
            return redirect(request.script_root + '/' + locale + '/')
    return redirect(request.script_root + '/' + current_app.config['LOCALES'].keys()[0] + '/')
