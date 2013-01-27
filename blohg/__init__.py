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
from flask import Flask, render_template, request
from flask.ctx import _app_ctx_stack
from flask.ext.babel import Babel
from jinja2.loaders import ChoiceLoader

# import blohg stuff
from blohg.ext import ExtensionImporter
from blohg.git import GitRepository
from blohg.git.changectx import ChangeCtxDefault as GitChangeCtxDefault
from blohg.hg import HgRepository
from blohg.models import Blog
from blohg.static import BlohgStaticFile
from blohg.templating import BlohgLoader
from blohg.vcs import REVISION_DEFAULT
from blohg.version import version as __version__
from blohg.views import views


class Blohg(object):

    def __init__(self, app, embedded_extensions=False):
        self.app = app
        self.embedded_extensions = embedded_extensions
        self.repo = load_repo(self.app.config['REPO_PATH'])
        self.changectx = None
        self.content = []
        app.blohg = self

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


def load_repo(repo_path):
    try:
        repo_root_files = os.listdir(repo_path)
    except:
        repo_root_files = []

    # try hg first, we are bloHG after all :)
    if '.hg' in repo_root_files:
        return HgRepository(repo_path)

    # try git workdir
    if '.git' in repo_root_files:
        return GitRepository(repo_path)

    # fallback to git bare repo, if available
    for f in ['config', 'info', 'objects']:
        if f not in repo_root_files:
            return

        # this is ugly, but we will force the default changectx here, because
        # bare repositories don't have an usable index :P
        class _GitRepository(GitRepository):
            def get_changectx(self, revision):
                return GitChangeCtxDefault(self.path)

        return _GitRepository(repo_path)


def create_app(repo_path=None, revision_id=REVISION_DEFAULT,
               autoinit=True, embedded_extensions=False):
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
    app.config.setdefault('EXTENSIONS', [])
    app.config.setdefault('EXTENSIONS_DIR', 'ext')

    app.config['REPO_PATH'] = repo_path

    blohg = Blohg(app, embedded_extensions)

    # setup our jinja2 custom loader and static file handlers
    old_loader = app.jinja_loader
    app.jinja_loader = ChoiceLoader([BlohgLoader(app), old_loader])
    app.add_url_rule(app.static_url_path + '/<path:filename>',
                     endpoint='static',
                     view_func=BlohgStaticFile(app, 'STATIC_DIR'))
    app.add_url_rule('/attachments/<path:filename>', endpoint='attachments',
                     view_func=BlohgStaticFile(app, 'ATTACHMENT_DIR'))

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

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    app.register_blueprint(views)

    if autoinit:
        blohg.init_repo(revision_id)

    return app
