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
import sys
import unittest
from flask import Flask

from blohg.ext import BlohgBlueprint, BlohgExtension, ExtensionImporter
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


class BlohgExtensionTestCase(unittest.TestCase):

    def test_g(self):
        app = Flask(__name__)
        with app.app_context():
            ext = BlohgExtension('blohg_foo')
            self.assertIsInstance(ext.g, app.app_ctx_globals_class)
            self.assertIs(ext.g, app._blohg_foo_globals)

    def test_setup_extension(self):
        app = Flask(__name__)
        with app.app_context():
            ext = BlohgExtension('blohg_foo')

            @ext.setup_extension
            def foo(inner_app):
                self.assertIs(inner_app, app)

            self.assertIn(foo, ext._callbacks)
            ext._load_extension(app)


class ExtensionImporterTestCase(unittest.TestCase):

    def setUp(self):
        self._meta_path = sys.meta_path[:]
        filectx_foo = mock.Mock(data="ext_id = 'foo'")
        filectx_bar = mock.Mock(data="ext_id = 'bar'")
        filectx_baz = mock.Mock(data="""\


raise RuntimeError('lol')
""")

        def get_filectx_side_effect(path):
            if path == 'ext/blohg_foo.py':
                return filectx_foo
            elif path == 'ext/blohg_bar/__init__.py':
                return filectx_bar
            elif path == 'ext/blohg_baz.py':
                return filectx_baz

        changectx = mock.Mock(files=['ext/blohg_foo.py',
                                     'ext/blohg_bar/__init__.py',
                                     'ext/blohg_baz.py'])
        changectx.get_filectx.side_effect = get_filectx_side_effect
        sys.meta_path[:] = [ExtensionImporter(changectx, 'ext')]

    def tearDown(self):
        sys.meta_path[:] = self._meta_path

    def test_import_module(self):
        import blohg_foo
        self.assertEquals(blohg_foo.ext_id, 'foo')
        del sys.modules['blohg_foo']

    def test_import_package(self):
        import blohg_bar
        self.assertEquals(blohg_bar.ext_id, 'bar')
        del sys.modules['blohg_bar']

    def test_import_broken_extension(self):
        try:
            __import__('blohg_baz')
        except RuntimeError:
            t, v, tb = sys.exc_info()
            self.assertEquals(tb.tb_next.tb_next.tb_frame.f_code.co_filename,
                              ':repo:ext/blohg_baz.py')
            self.assertEquals(tb.tb_next.tb_next.tb_frame.f_lineno, 3)
        else:
            self.fail('Exception not raised!')
        del sys.modules['blohg_baz']

    def test_invalid_import(self):
        with self.assertRaises(ImportError):
            __import__('blohg_lol')
