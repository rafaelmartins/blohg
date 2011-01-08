# -*- coding: utf-8 -*-
"""
    blohg
    ~~~~~
    
    Main package.
    
    :copyright: (c) 2010-2011 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from flask import Flask, render_template, request
from flaskext.babel import Babel

# import blohg stuff
from blohg.filters import rst2html, tag_name, append_title
from blohg.mercurial_content import setup_mercurial
from blohg.mercurial_theme import setup_theme
from blohg.version import version as __version__
from blohg.views import views


def create_app(repo_path=None):
    """Application factory.
    
    :param repo_path: the path to the mercurial repository.
    :return: the WSGI application (Flask instance).
    """
    
    # create the app object
    app = Flask(__name__)
    
    # register some sane default config values
    app.config.setdefault('AUTHOR', 'Your Name Here')
    app.config.setdefault('POSTS_PER_PAGE', 10)
    app.config.setdefault('REPO_PATH', repo_path)
    app.config.setdefault('TAGLINE', u'Your cool tagline')
    app.config.setdefault('TAGS', {})
    app.config.setdefault('TITLE', u'Your title')
    app.config.setdefault('TITLE_HTML', u'Your HTML title')
    app.config.setdefault('TEMPLATES_DIR', 'templates')
    app.config.setdefault('STATIC_DIR', 'static')
    
    # init mercurial stuff
    setup_mercurial(app)
    
    # setup extensions
    setup_theme(app)
    babel = Babel(app)
    
    # setup jinja2 filters
    app.jinja_env.filters.update(
        rst2html = rst2html,
        tag_name = tag_name,
        append_title = append_title,
    )
    
    @app.context_processor
    def setup_jinja2():
        return dict(
            version = __version__,
            is_post = lambda x: x.startswith('post/'),
            current_path = request.path.strip('/'),
            active_page = request.path.strip('/').split('/')[0],
            tags = app.hg.tags,
            config = app.config,
        )
    
    @babel.timezoneselector
    def get_timezone():
        return app.config['TIMEZONE']
    
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404
    
    app.register_module(views)
    
    return app
