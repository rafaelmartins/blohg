# -*- coding: utf-8 -*-
"""
    blohg.tests.ext
    ~~~~~~~~~~~~~~~

    Module with tests for blohg's support for 3rd-party extensions.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import mock
import os
import unittest
from flask import Flask

from blohg.ext import BlohgBlueprint
from blohg.static import BlohgStaticFile
from blohg.templating import BlohgLoader

cwd = os.path.dirname(os.path.abspath(__file__))


class BlohgBlueprintTestCase(unittest.TestCase):

    def test_jinja_loader_from_disk(self):
        bp = BlohgBlueprint('foo', __name__, template_folder='templ')
        fake_dir = os.path.join(cwd, 'templ')
        self.assertEquals(len(bp.jinja_loader.searchpath), 1)
        self.assertEquals(bp.jinja_loader.searchpath[0], fake_dir)

    @mock.patch('flask.helpers.get_root_path')
    def test_jinja_loader_from_repo_package(self, get_root_path):
        get_root_path.return_value = ':repo:ext/blohg_foo'
        bp = BlohgBlueprint('foo', __name__, template_folder='templ')
        self.assertIsInstance(bp.jinja_loader, BlohgLoader)
        self.assertEquals(bp.jinja_loader.template_folder,
                          'ext/blohg_foo/templ')

    @mock.patch('flask.helpers.get_root_path')
    def test_jinja_loader_from_repo_module(self, get_root_path):
        get_root_path.return_value = ':repo:ext'
        bp = BlohgBlueprint('foo', __name__, template_folder='templ')
        self.assertIsInstance(bp.jinja_loader, BlohgLoader)
        self.assertEquals(bp.jinja_loader.template_folder, 'ext/templ')

    def test_static_folder_from_disk(self):
        bp = BlohgBlueprint('foo', __name__, static_folder='st')
        app = Flask(__name__)
        app.register_blueprint(bp)
        view_func = app.view_functions['foo.static']
        # poor test, but should be enough :)
        self.assertEquals(view_func.__name__, 'send_static_file')

    @mock.patch('flask.helpers.get_root_path')
    def test_static_folder_from_repo_package(self, get_root_path):
        get_root_path.return_value = ':repo:ext/blohg_foo'
        bp = BlohgBlueprint('foo', __name__, static_folder='st')
        app = Flask(__name__)
        app.register_blueprint(bp)
        view_func = app.view_functions['foo.static']
        self.assertIsInstance(view_func, BlohgStaticFile)
        self.assertEquals(view_func.directory, 'ext/blohg_foo/st')

    @mock.patch('flask.helpers.get_root_path')
    def test_static_folder_from_repo_module(self, get_root_path):
        get_root_path.return_value = ':repo:ext'
        bp = BlohgBlueprint('foo', __name__, static_folder='st')
        app = Flask(__name__)
        app.register_blueprint(bp)
        view_func = app.view_functions['foo.static']
        self.assertIsInstance(view_func, BlohgStaticFile)
        self.assertEquals(view_func.directory, 'ext/st')
