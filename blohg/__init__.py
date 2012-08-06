# -*- coding: utf-8 -*-
"""
    blohg
    ~~~~~

    Main package.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from flask import Flask, render_template, request
from flask.ext.babel import Babel

# import blohg stuff
from blohg.hgapi import setup_mercurial
from blohg.version import version as __version__
from blohg.views import views


def create_app(repo_path=None, hgui=None):
    """Application factory.

    :param repo_path: the path to the mercurial repository.
    :return: the WSGI application (Flask instance).
    """

    # create the app object
    app = Flask(__name__)

    # register some sane default config values
    app.config.setdefault('AUTHOR', u'Your Name Here')
    app.config.setdefault('POSTS_PER_PAGE', 10)
    app.config.setdefault('TAGLINE', u'Your cool tagline')
    app.config.setdefault('TITLE', u'Your title')
    app.config.setdefault('TITLE_HTML', u'Your HTML title')
    app.config.setdefault('CONTENT_DIR', u'content')
    app.config.setdefault('TEMPLATES_DIR', u'templates')
    app.config.setdefault('STATIC_DIR', u'static')
    app.config.setdefault('ATTACHMENT_DIR', u'content/attachments')
    app.config.setdefault('ROBOTS_TXT', True)
    app.config.setdefault('SHOW_RST_SOURCE', True)
    app.config.setdefault('POST_EXT', u'.rst')
    app.config.setdefault('OPENGRAPH', True)
    app.config.setdefault('TIMEZONE', 'UTC')
    app.config.setdefault('RST_HEADER_LEVEL', 3)

    app.config['REPO_PATH'] = repo_path

    # init mercurial stuff
    setup_mercurial(app, hgui=hgui)

    # setup extensions
    babel = Babel(app)

    @app.context_processor
    def setup_jinja2():
        return dict(
            version=__version__,
            is_post=lambda x: x.startswith('post/'),
            current_path=request.path.strip('/'),
            active_page=request.path.strip('/').split('/')[0],
            tags=app.hg.tags,
            config=app.config,
        )

    @babel.timezoneselector
    def get_timezone():
        return app.config['TIMEZONE']

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    app.register_blueprint(views)

    return app
