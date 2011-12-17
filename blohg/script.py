# -*- coding: utf-8 -*-
"""
    blohg.script
    ~~~~~~~~~~~~

    Module with the CLI script related stuff.

    :copyright: (c) 2010-2011 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
import sys
import posixpath
from flask_frozen import Freezer
from flaskext.script import Command, Manager, Server, Option
from werkzeug.routing import Map

from blohg import create_app
from blohg.utils import create_repo


class InitRepo(Command):
    """initialize a blohg repo, using the default template."""

    def handle(self, app):
        try:
            create_repo(app)
        except RuntimeError, err:
            print >> sys.stderr, str(err)


class Freeze(Command):
    """ freeze the blog into a set of static files. """

    option_list = (
        Option('--serve', '-s', dest='serve', default=False,
                action='store_true'),
        Option('--noindex', dest='no_index', default=False,
                action='store_true')
    )

    def remap_rules(self, map, map_html):
        """ remaping the rules with files extensions """
        mapping = {'views.source': 'txt',
                   'views.atom': 'atom'}
        if map_html:
            mapping['views.tag'] = 'html'
            mapping['views.content'] = 'html'
            mapping['views.post_list'] = 'html'
            mapping['views.posts'] = 'html'
            mapping['views.home'] = 'html'
        rules = []
        for rule in map.iter_rules():
            rule = rule.empty()
            if rule.is_leaf:
                # Add the leafs without modif.
                rules.append(rule)
                continue

            # special treatment for the robot.txt url
            if rule.rule == '/source/':
                rules.append(rule)
                continue

            try:
                extension = mapping[rule.endpoint]
            except KeyError:
                # the rest can go through
                rules.append(rule)
                continue
            # It becomes a leaf
            rule.is_leaf = True
            # and we add an extension
            url = rule.rule[:-1]
            if url == "":
                url = '/index'
            rule.rule = url+'.'+extension
            # and we add the modified rule
            rules.append(rule)
        return Map(rules)

    def handle(self, app, serve, no_index):

        app.url_map = self.remap_rules(app.url_map, no_index)

        # That's a risky one, it woud be better to give a parameter to the
        # freezer
        app.root_path = app.config.get('REPO_PATH')

        freezer = Freezer(app)

        @freezer.register_generator
        def static():
            """ Walk the static dir and freeze everything """
            static_path = os.path.join(app.config.get('REPO_PATH'),
                                             app.config['STATIC_DIR'])
            for root, dirs, files in os.walk(static_path):
                for f in files:
                    # make it relative
                    path = posixpath.join(root,f)[len(static_path) + 1:]
                    yield {'filename': path}

        freezer.freeze()
        if serve:
            freezer.serve()


def create_script():
    """Script object factory

    :param repo_path: the path to the mercurial repository.
    :return: the script object (Flask-Script' Manager instance).
    """

    script = Manager(create_app, with_default_commands=False)
    script.add_option('-r', '--repo-path', dest='repo_path', default=os.getcwd(),
        required=False)
    server = Server(use_debugger=True, use_reloader=True)
    server.description = 'runs the blohg local server.'
    script.add_command('runserver', server)
    script.add_command('initrepo', InitRepo())
    script.add_command('freeze', Freeze())

    return script
