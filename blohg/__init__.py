# -*- coding: utf-8 -*-

import re

from flask import Flask, request, abort
from flaskext.babel import Babel
from flaskext.themes import setup_themes, render_theme_template

# import blohg stuff
from blohg.mercurial_content import setup_mercurial
from blohg.filters import rst2html, tag_name

# import blohg views
from blohg.views.atom import atom
from blohg.views.pages import pages
from blohg.views.posts import posts
from blohg.views.robots import robots
from blohg.views.source import source

__version__ = '0.1pre'

_en_us_locale = {
    'locale': 'en_US',
    'name': 'English',
}

def create_app(config_file=None):
    
    # create the app object
    app = Flask('blohg')
    
    # register some sane default config values
    app.config.setdefault('REPO_PATH', '.')
    app.config.setdefault('LOCALES', {'en-us': _en_us_locale})
    app.config.setdefault('TITLE', {'en_US': u'Your title'})
    app.config.setdefault('TITLE_HTML', {'en_US': u'Your HTML title'})
    app.config.setdefault('TAGLINE', {'en_US': u'Your cool tagline'})
    app.config.setdefault('MENU', {'en_US': []})
    app.config.setdefault('SIDEBAR', {'en_US': []})
    app.config.setdefault('POSTS_PER_PAGE', 10)
    app.config.setdefault('THEME', 'basic')
    app.config.setdefault('TAGS', {})
    app.config.setdefault('AUTHOR', 'Your Name Here')
    
    # load configs from a file, if needed
    if config_file is not None:
        app.config.from_pyfile(config_file)

    babel = Babel(app)
    setup_themes(app)
    setup_mercurial(app)
    
    app.jinja_env.filters.update(
        rst2html = rst2html,
        tag_name = tag_name,
    )
    
    @app.context_processor
    def setup_jinja2():
        return dict(
            version = __version__,
            localized_config = localized_config,
            is_post = lambda x: x.startswith('post/'),
            my_locale = my_locale(),
            current_path = current_path(),
            active_page = active_page(),
            tags = app.hg.get_tags(my_locale()),
        )
    
    def my_locale():
        match = re.match(r'/([^/]+).*', request.path)
        if match is not None:
            return match.group(1)
        return 'en-us'
    
    def current_path():
        match = re.match(r'/[^/]+/(.+)/', request.path)
        if match is not None:
            return match.group(1)
        return ''
    
    def active_page():
        return current_path().split('/')[0]

    @babel.localeselector
    def get_locale():
        return app.config['LOCALES'].get(my_locale(), _en_us_locale)['locale']
    
    def localized_config(key):
        config = app.config.get(key, None)
        if config is None:
            return None
        locale = get_locale()
        if locale in config:
            return config[locale]
        if type(config) == dict:
            return config.values()[0]
        return config
    app.localized_config = localized_config
    
    def validate_locale(f):
        def new_f(*args, **kwargs):
            match = re.match(r'/([^/]+).*', request.path)
            print match
            if match is not None:
                locale = match.group(1)
                if locale not in current_app.config['LOCALES']:
                    return 'fail', 404
            return f(*args, **kwargs)
        return new_f
    app.validate_locale = validate_locale
    
    @app.errorhandler(404)
    def page_not_found(error):
        return render_theme_template(
            app.config['THEME'],
            '404.html'
        ), 404
    
    app.register_module(robots)
    app.register_module(source)
    app.register_module(posts)
    app.register_module(pages)
    app.register_module(atom)
    
    return app
