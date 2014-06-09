# -*- coding: utf-8 -*-
"""
    blohg.script
    ~~~~~~~~~~~~

    Module with the CLI script related stuff.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import click
import os
import sys
import posixpath
from flask_frozen import Freezer, MissingURLGeneratorWarning
from warnings import filterwarnings
from werkzeug.routing import Map

from blohg import create_app
from blohg.vcs import backends, REVISION_DEFAULT, REVISION_WORKING_DIR

# filter MissingURLGeneratorWarning warnings.
filterwarnings('ignore', category=MissingURLGeneratorWarning)


def _create_app(repo_path, disable_embedded_extensions):
    return create_app(repo_path=os.path.abspath(repo_path), autoinit=False,
                      embedded_extensions=not disable_embedded_extensions,
                      debug=True)


@click.group()
def cli():
    '''blohg's command line interface'''


@cli.command()
@click.option('--repo-path', default='.', metavar='REPO_PATH',
              help='Repository path.')
@click.option('--disable-embedded-extensions', is_flag=True,
              help='Disable embedded extensions.')
@click.option('--serve', '-s', is_flag=True,
              help='Run development server.')
@click.option('--noindex', is_flag=True,
              help='Create standalone HTML files, instead of dirs with '
              'index.html.')
def freeze(repo_path, disable_embedded_extensions, serve, noindex):
    '''Freeze the blog into a set of static files.'''

    app = _create_app(repo_path, disable_embedded_extensions)

    def remap_rules(map, map_html):
        """remaping the rules with files extensions"""
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
            if url == '':
                url = '/index'
            rule.rule = url + '.' + extension
            # and we add the modified rule
            rules.append(rule)
        return Map(rules)

    app.blohg.init_repo(REVISION_DEFAULT)
    app.url_map = remap_rules(app.url_map, noindex)
    app.config.setdefault('FREEZER_DESTINATION', os.path.join(
        app.config.get('REPO_PATH'), 'build'))

    freezer = Freezer(app)

    def static_generator(static_dir):
        for f in app.blohg.changectx.files:
            if f.startswith(static_dir):
                yield dict(filename=f[len(static_dir):] \
                           .strip(posixpath.sep))

    @freezer.register_generator
    def static():
        '''Walk the static dir and freeze everything'''
        return static_generator('static')

    @freezer.register_generator
    def attachments():
        '''Walk the attachment dir and freeze everything'''
        return static_generator(app.config['ATTACHMENT_DIR'])

    freezer.freeze()
    if serve:
        freezer.serve()


@cli.command()
@click.option('--repo-path', default='.', metavar='REPO_PATH',
              help='Repository path.')
def initrepo(repo_path, vcs):
    '''Initialize a blohg repo, using the default template.'''

    repo = None
    for backend in backends:
        if backend.identifier == vcs:
            repo = backend
            break
    try:
        if repo is None:
            if vcs is None and len(backends) > 0:
                repo = backends[0]
            else:
                raise RuntimeError('No VCS backend found for repository: %s'
                                   % repo_path)
        repo.create_repo(os.path.abspath(repo_path))
    except RuntimeError, err:
        click.echo(str(err), file=sys.stderr)

for backend in backends:
    # decorating the function like a boss :P
    initrepo = click.option('--%s' % backend.identifier, 'vcs',
                            flag_value=backend.identifier,
                            help='Create a %s repository'
                            % backend.name)(initrepo)


@cli.command()
@click.option('--repo-path', default='.', metavar='REPO_PATH',
              help='Repository path.')
@click.option('--disable-embedded-extensions', is_flag=True,
              help='Disable embedded extensions.')
@click.option('--revision-default', '-n', is_flag=True,
              help='Use files from the default branch, instead of the '
              'working directory.')
@click.option('--host', '-t', default='127.0.0.1', metavar='HOST',
              help='Server host.')
@click.option('--port', '-p', type=click.INT, default=5000, metavar='PORT',
              help='Server port.')
@click.option('--threaded', is_flag=True,
              help='Handle each request in a separate thread.')
@click.option('--processes', type=click.INT, default=1, metavar='PROCESSES',
              help='Number of processes to spawn.')
@click.option('--passthrough-errors', is_flag=True,
              help='Disable the error catching.')
@click.option('--no-debug', '-d', is_flag=True,
              help='Disable Werkzeug debugger.')
@click.option('--no-reload', '-r', is_flag=True,
              help='Disable automatic reloader.')
def runserver(repo_path, disable_embedded_extensions, revision_default, host,
              port, threaded, processes, passthrough_errors, no_debug,
              no_reload):
    '''Run the blohg development server.'''

    app = _create_app(repo_path, disable_embedded_extensions)

    revision_id = REVISION_WORKING_DIR
    if revision_default:
        revision_id = REVISION_DEFAULT
    use_debugger = not no_debug
    use_reloader = not no_reload

    os.environ['RUNNING_FROM_CLI'] = '1'
    app.blohg.init_repo(revision_id)

    # find extension files
    def _listfiles(directory, files):
        if not os.path.exists(directory):
            return
        for f in os.listdir(directory):
            fname = os.path.join(directory, f)
            if os.path.isdir(fname):
                _listfiles(fname, files)
            else:
                files.append(os.path.abspath(fname))

    extra_files = []
    _listfiles(os.path.join(app.config['REPO_PATH'],
                            app.config['EXTENSIONS_DIR']), extra_files)

    app.run(host=host, port=port, debug=use_debugger,
            use_debugger=use_debugger, use_reloader=use_reloader,
            threaded=threaded, processes=processes,
            passthrough_errors=passthrough_errors, extra_files=extra_files)
