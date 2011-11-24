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
from flaskext.script import Command, Manager, Server, Option

from blohg import create_app
from blohg.utils import create_repo

from flask_frozen import Freezer

from werkzeug.routing import Map


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
    )

    def remap_rules(self, map):
        """ remaping the rules with files extensions """
        rules = []
        for rule in map.iter_rules():
            rule = rule.empty()
            if rule.is_leaf:
                # Add the leafs without modif.
                rules.append(rule)
                continue

            if rule.rule == '/source/':
                print "adding %s" % rule.rule
                rules.append(rule)
                continue

            try:
                extension = {'views.source': 'txt',
                             'views.atom': 'atom',
                             'views.tag':'html',
                             'views.content': 'html'}[rule.endpoint]
            except KeyError:
                # the rest can go through
                rules.append(rule)
                continue
            # It becomes a leaf
            rule.is_leaf = True
            # and we add an extension
            url = rule.rule[:-1]
            rule.rule = url+'.'+extension
            # and we add the modified rule
            rules.append(rule)
        return Map(rules)

    def handle(self, app, serve):

        app.url_map = self.remap_rules(app.url_map)

        print app.url_map

        freezer = Freezer(app)
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
