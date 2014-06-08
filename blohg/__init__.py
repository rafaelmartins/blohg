# -*- coding: utf-8 -*-
"""
    blohg
    ~~~~~

    Main package.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
import yaml
from flask import Flask as _Flask, render_template, request
from flask.ctx import _app_ctx_stack
from flask.ext.babel import Babel
from flask.helpers import locked_cached_property
from jinja2.loaders import ChoiceLoader

# import blohg stuff
from blohg.ext import ExtensionImporter
from blohg.models import Blog
from blohg.signals import reloaded
from blohg.static import BlohgStaticFile
from blohg.templating import BlohgLoader
from blohg.vcs import load_repo, REVISION_DEFAULT
from blohg.version import version as __version__
from blohg.views import views


class Flask(_Flask):

    @locked_cached_property
    def jinja_loader(self):
        if self.template_folder is not None:
            return ChoiceLoader([BlohgLoader(self.template_folder),
                                 super(_Flask, self).jinja_loader])


class Blohg(object):

    def __init__(self, app, embedded_extensions=False):
        self.app = app
        self.embedded_extensions = embedded_extensions
        self.changectx = None
        self.content = []
        app.blohg = self

    @locked_cached_property
    def repo(self):
        if not os.path.isdir(self.app.config['REPO_PATH']):
            raise RuntimeError('Repository not found: %s' % \
                               self.app.config['REPO_PATH'])
        return load_repo(self.app.config['REPO_PATH'])

    def init_repo(self, revision_id):
        if not os.path.isdir(self.app.config['REPO_PATH']):
            raise RuntimeError('Repository not found: %s' % \
                               self.app.config['REPO_PATH'])
        self.revision_id = revision_id
        self.reload()
        self.load_extensions()

    def _load_config(self):
        config = yaml.load(self.changectx.get_filectx('config.yaml').content)

        # monkey-patch configs when running from built-in server
        if 'RUNNING_FROM_CLI' in os.environ:
            if 'GOOGLE_ANALYTICS' in config:
                del config['GOOGLE_ANALYTICS']
            config['DISQUS_DEVELOPER'] = True

        self.app.config.update(config)

    def reload(self):

        # if called from the initrepo script command the repository will not
        # exists, then it shouldn't be loaded
        if not os.path.exists(self.app.config['REPO_PATH']):
            return

        if self.changectx is not None and not self.changectx.needs_reload():
            return

        self.changectx = self.repo.get_changectx(self.revision_id)
        self._load_config()

        # build a regular expression for search posts/pages.
        content_dir = self.app.config['CONTENT_DIR']
        post_ext = self.app.config['POST_EXT']
        rst_header_level = self.app.config['RST_HEADER_LEVEL']

        self.content = Blog(self.changectx, content_dir, post_ext,
                            rst_header_level)

        reloaded.send(self)

    def load_extensions(self):
        if self.embedded_extensions:
            ExtensionImporter.new(self.changectx,
                                  self.app.config['EXTENSIONS_DIR'])
        with self.app.app_context():
            for ext in self.app.config['EXTENSIONS']:
                __import__('blohg_%s' % ext)
            ctx = _app_ctx_stack.top
            if hasattr(ctx, 'extension_registry'):
                for ext in ctx.extension_registry:
                    ext._load_extension(self.app)


def create_app(repo_path=None, revision_id=REVISION_DEFAULT,
               autoinit=True, embedded_extensions=False, debug=False):
    """Application factory.

    :param repo_path: the path to the mercurial repository.
    :return: the WSGI application (Flask instance).
    """

    # create the app object
    app = Flask(__name__, static_folder=None)
    app.debug = debug

    # register some sane default config values
    app.config.setdefault('AUTHOR', u'Your Name Here')
    app.config.setdefault('POSTS_PER_PAGE', 10)
    app.config.setdefault('TAGLINE', u'Your cool tagline')
    app.config.setdefault('TITLE', u'Your title')
    app.config.setdefault('TITLE_HTML', u'Your HTML title')
    app.config.setdefault('CONTENT_DIR', u'content')
    app.config.setdefault('ATTACHMENT_DIR', u'content/attachments')
    app.config.setdefault('ROBOTS_TXT', True)
    app.config.setdefault('SHOW_RST_SOURCE', True)
    app.config.setdefault('POST_EXT', u'.rst')
    app.config.setdefault('OPENGRAPH', True)
    app.config.setdefault('TIMEZONE', 'UTC')
    app.config.setdefault('LOCALE', 'en')
    app.config.setdefault('RST_HEADER_LEVEL', 3)
    app.config.setdefault('EXTENSIONS', [])
    app.config.setdefault('EXTENSIONS_DIR', 'ext')

    app.config['REPO_PATH'] = repo_path

    blohg = Blohg(app, embedded_extensions)

    app.add_url_rule('/static/<path:filename>', endpoint='static',
                     view_func=BlohgStaticFile('static'))
    app.add_url_rule('/attachments/<path:filename>', endpoint='attachments',
                     view_func=BlohgStaticFile(app.config['ATTACHMENT_DIR']))

    # setup extensions
    babel = Babel(app)

    @app.before_request
    def before_request():
        app.blohg.reload()

    @app.context_processor
    def setup_jinja2():
        return dict(
            version=__version__,
            is_post=lambda x: x.startswith('post/'),
            current_path=request.path.strip('/'),
            active_page=request.path.strip('/').split('/')[0],
            tags=app.blohg.content.tags,
            config=app.config,
        )

    @babel.timezoneselector
    def get_timezone():
        return app.config['TIMEZONE']

    @babel.localeselector
    def get_locale():
        return app.config['LOCALE']

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    app.register_blueprint(views)

    if autoinit:
        blohg.init_repo(revision_id)

    return app
