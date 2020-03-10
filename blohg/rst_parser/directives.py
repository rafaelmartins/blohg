# -*- coding: utf-8 -*-
"""
    blohg.rst_parser.directives
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Module with the custom blohg reStructuredText directives.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from docutils import nodes, statemachine
from docutils.utils.error_reporting import ErrorString
from docutils.io import FileInput
from docutils.parsers.rst import directives, Directive
from docutils.parsers.rst.directives.images import Image, Figure
from docutils.parsers.rst.directives.misc import Include
from flask import current_app, url_for
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer
from urllib.request import pathname2url

from blohg.file_like import BlohgFile
from blohg.rst_parser.nodes import iframe_flash_video

import posixpath


__all__ = ['Vimeo', 'Youtube', 'Math', 'MathJax', 'Code', 'SourceCode', 'AttachmentImage',
           'AttachmentFigure', 'SubPages', 'IncludeHg']

GOOGLETEX_URL = 'https://chart.googleapis.com/chart?cht=tx&chl='


def align(argument):
    return directives.choice(argument, ('left', 'center', 'right'))


def boolean(argument):
    return directives.choice(argument, ('true', 'false'))


class Vimeo(Directive):
    """reStructuredText directive that creates an embed object to display
    a video from Vimeo

    Usage example::

        .. vimeo:: QFwQIRwuAM0
           :align: center
           :height: 344
           :width: 425
    """

    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        'height': directives.length_or_unitless,
        'width': directives.length_or_percentage_or_unitless,
        'border': directives.length_or_unitless,
        'align': align,
        'allowfullscreen': boolean,
    }
    has_content = False

    def run(self):
        self.options['uri'] = 'http://player.vimeo.com/video/' \
            + self.arguments[0]
        self.options.setdefault('width', '425px')
        self.options.setdefault('height', '344px')
        self.options.setdefault('align', 'center')
        self.options.setdefault('border', '0')
        self.options.setdefault('allowfullscreen', 'true')
        return [iframe_flash_video('', **self.options)]


class Youtube(Directive):
    """reStructuredText directive that creates an embed object to display
    a video from Youtube

    Usage example::

        .. youtube:: QFwQIRwuAM0
           :align: center
           :height: 344
           :width: 425
    """

    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        'height': directives.length_or_unitless,
        'width': directives.length_or_percentage_or_unitless,
        'border': directives.length_or_unitless,
        'align': align,
        'allowfullscreen': boolean,
    }
    has_content = False

    def run(self):
        self.options['uri'] = 'http://www.youtube.com/embed/%s' % \
            self.arguments[0]
        self.options['thumbnail_uri'] = \
            'http://img.youtube.com/vi/%s/hqdefault.jpg' % self.arguments[0]
        self.options.setdefault('width', '425px')
        self.options.setdefault('height', '344px')
        self.options.setdefault('align', 'center')
        self.options.setdefault('border', '0')
        self.options.setdefault('allowfullscreen', 'true')
        return [iframe_flash_video('', **self.options)]


class Code(Directive):
    """reStructuredText directive that creates a pre tag suitable for
    decoration with http://alexgorbatchev.com/SyntaxHighlighter/

    Usage example::

        .. source:: python

           print "Hello, World!"

        .. raw:: html

            <script type="text/javascript" src="http://alexgorbatchev.com/pub/sh/current/scripts/shCore.js"></script>
            <script type="text/javascript" src="http://alexgorbatchev.com/pub/sh/current/scripts/shBrushPython.js"></script>
            <link type="text/css" rel="stylesheet" href="http://alexgorbatchev.com/pub/sh/current/styles/shCoreDefault.css"/>
            <script type="text/javascript">SyntaxHighlighter.defaults.toolbar=false; SyntaxHighlighter.all();</script>

    """

    required_arguments = 1
    optional_arguments = 0
    has_content = True

    def run(self):
        self.assert_has_content()
        self.options['brush'] = self.arguments[0]
        html = '''\

<pre class="brush: %s">
%s
</pre>

'''
        return [nodes.raw('', html % (self.options['brush'],
            "\n".join(self.content).replace('<', '&lt;')),
            format='html')]


class SourceCode(Directive):
    """reStructuredText directive that does syntax highlight using Pygments.

    Usage example::

        .. sourcecode:: python
           :linenos:

            print "Hello, World!"

    The ``linenos`` option enables the line numbering.

    To be able to use this directive you should generate a CSS file with the
    style definitions, using the ``pygmentize`` script, shipped with Pygments.

    ::

        $ pygmentize -S friendly -f html > static/pygments.css

    Where ``friendly`` will be your Pygments style of choice.

    This file should be included in the main template, usually ``base.html``::

        <link type="text/css" media="screen" rel="stylesheet" href="{{
            url_for('static', filename='pygments.css') }}" />

    This directive is based on ``rst-directive.py``, created by Pygments
    authors.
    """

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'linenos': directives.flag,
    }
    has_content = True

    def run(self):
        self.assert_has_content()
        try:
            lexer = get_lexer_by_name(self.arguments[0])
        except ValueError:
            # no lexer found - use the text one instead of an exception
            lexer = TextLexer()
        formatter = HtmlFormatter(noclasses=False)
        if 'linenos' in self.options:
            formatter.linenos = 2  # inline
        parsed = highlight('\n'.join(self.content), lexer, formatter)
        return [nodes.raw('', parsed, format='html')]


class Math(Image):
    """reStructuredText directive that creates an image HTML object to
    display a LaTeX equation, using Google Chart API.

    Usage example::

        .. math::

            \\frac{x^2}{1+x}
    """

    required_arguments = 0
    has_content = True

    def run(self):
        self.assert_has_content()
        if not 'align' in self.options:
            self.options['align'] = 'center'
        tmp = pathname2url(' '.join([(i == '' and '\\\\' or i.strip()) \
            for i in self.content]))
        self.arguments.append('%s%s' % (GOOGLETEX_URL, tmp))
        return Image.run(self)


class MathJax(Directive):
    """reStructuredText directive that simply returns a math html fragment suitable for rendering by MathJax.

    The latex math equations are simply wrapped by an HTML div tag with mathjax class for further CSS decoration.
    Use conventional LaTeX to write math equations.
    Note that $ signs or \\begin{equation} etc. should be no longer omitted.
    Auto-numbering is possible by configuring MathJax before loading MathJax, via::

        <script type="text/x-mathjax-config">
            MathJax.Hub.Config({
                TeX: { equationNumbers: { autoNumber: "AMS" } }
            });
        </script>

    Usage example::

        .. mathjax::

            $$\\frac{x^2}{1+x}\\label{frac_eq}$$

    for a displayed numbered equation with a reference. Use "\\eqref{frac_eq}" in normal way to cite the equation number.
    LaTeX math \\begin{equation}, \\begin{align}, etc. are all supported.
    See MathJax official websites for more information.
    """

    required_arguments = 0
    has_content = True

    def run(self):
        self.assert_has_content()
        html = '''\

<div class="mathjax">
%s
</div>

'''
        return [nodes.raw('', html % (
            "\n".join(self.content).replace('<', '&lt;'), ),
            format='html')]


class AttachmentImage(Image):

    def run(self):
        my_file = directives.uri(self.arguments[0])
        full_path = posixpath.join(current_app.config['ATTACHMENT_DIR'],
                                   my_file)
        if full_path not in current_app.blohg.changectx.files:
            raise self.error(
                'Error in "%s" directive: File not found: %s.' % (
                    self.name, full_path
                )
            )
        self.arguments[0] = url_for('attachments', filename=my_file,
                                    _external=True)
        return Image.run(self)


class AttachmentFigure(Figure):

    def run(self):
        my_file = directives.uri(self.arguments[0])
        full_path = posixpath.join(current_app.config['ATTACHMENT_DIR'],
                                   my_file)
        if full_path not in current_app.blohg.changectx.files:
            raise self.error(
                'Error in "%s" directive: File not found: %s.' % (
                    self.name, full_path
                )
            )
        self.arguments[0] = url_for('attachments', filename=my_file,
                                    _external=True)
        return Figure.run(self)


class SubPages(Directive):
    """reStructuredText directive that creates a bullet-list with the subpages
    of the current page, or of a given page.

    Usage example::

        .. subpages::

    Or::

        .. subpages:: projects

    Supposing that you have a directory called ``content/projects`` and some
    reStructuredText files on it. Subdirectories are also allowed.

    It is also possible to change the way the bullet-list is sorted, using the
    options ``sort-by`` and ``sort-order``::

        .. subpages::
           :sort-by: slug
           :sort-order: desc

    Available options for ``sort-by`` are ``slug`` (default option), ``title``
    and ``date``, and for ``sort-order`` are ``asc`` (default option) and
    ``desc``.

    This directive will just show the files from the root of the directory.
    It's not recursive.
    """

    required_arguments = 0
    optional_arguments = 1
    option_spec = {
        'sort-by': lambda x: directives.choice(x, ('slug', 'title', 'date')),
        'sort-order': lambda x: directives.choice(x, ('asc', 'desc'))
    }
    has_content = False

    def run(self):
        self.options.setdefault('sort-by', 'slug')
        self.options.setdefault('sort-order', 'asc')
        if len(self.arguments) == 0:
            prefix = ':repo:%s' % current_app.config['CONTENT_DIR']
            source = self.state.document.current_source or ''
            if not source.startswith(prefix):
                raise self.severe('Problem with "%s" directive path:\npath ' \
                                  'isn\'t allowed: %s' % (self.name, source))
            source = source[len(prefix)+1:]
            source = source.rstrip('/index%s' % current_app.config['POST_EXT'])
            source = source.rstrip(current_app.config['POST_EXT'])
            self.arguments.append(source)
        tmp_metadata = []
        final_metadata = []
        splited_dir = len(self.arguments[0]) > 0 \
            and self.arguments[0].split('/') or []
        for metadata in current_app.blohg.content.get_all():
            splited_slug = metadata.slug.split('/')
            if metadata.slug.startswith(self.arguments[0]) and \
               (len(splited_dir) + 1 == len(splited_slug)):
                tmp_metadata.append(metadata)

        def key_func(metadata):
            if self.options['sort-by'] == 'title':
                return metadata.get('link_title', metadata.title)
            return getattr(metadata, self.options['sort-by'])

        for metadata in sorted(tmp_metadata, key=key_func,
                               reverse=(self.options['sort-order'] == 'desc')):
            link = url_for('views.content', slug=metadata.slug)
            link_title = metadata.get('link_title', metadata.title)
            reference = nodes.reference(link, link_title, refuri=link)
            final_metadata.append(nodes.list_item('',
                                                  nodes.paragraph('', '',
                                                                  reference)))
        return [nodes.bullet_list('', *final_metadata)]


class IncludeHg(Include):

    def run(self):
        if not self.state.document.settings.file_insertion_enabled:
            raise self.warning('"%s" directive disabled.' % self.name)
        path = directives.path(self.arguments[0])
        # ALL the included files are relative to the repository root.
        # we need to remove absolute paths
        if path.startswith('/'):
            raise self.severe('Problem with "%s" directive path:\npath ' \
                              'should be relative' % self.name)
        encoding = self.options.get(
            'encoding', self.state.document.settings.input_encoding)
        tab_width = self.options.get(
            'tab-width', self.state.document.settings.tab_width)
        try:
            self.state.document.settings.record_dependencies.add(path)
            include_file = FileInput(
                source=BlohgFile(path), encoding=encoding,
                error_handler=(self.state.document.settings.\
                               input_encoding_error_handler))
        except IOError as error:
            raise self.severe('Problems with "%s" directive path:\n%s.' %
                      (self.name, ErrorString(error)))
        startline = self.options.get('start-line', None)
        endline = self.options.get('end-line', None)
        try:
            if startline or (endline is not None):
                lines = include_file.readlines()
                rawtext = ''.join(lines[startline:endline])
            else:
                rawtext = include_file.read()
        except UnicodeError as error:
            raise self.severe('Problem with "%s" directive:\n%s' %
                              (self.name, ErrorString(error)))
        # start-after/end-before: no restrictions on newlines in match-text,
        # and no restrictions on matching inside lines vs. line boundaries
        after_text = self.options.get('start-after', None)
        if after_text:
            # skip content in rawtext before *and incl.* a matching text
            after_index = rawtext.find(after_text)
            if after_index < 0:
                raise self.severe('Problem with "start-after" option of "%s" '
                                  'directive:\nText not found.' % self.name)
            rawtext = rawtext[after_index + len(after_text):]
        before_text = self.options.get('end-before', None)
        if before_text:
            # skip content in rawtext after *and incl.* a matching text
            before_index = rawtext.find(before_text)
            if before_index < 0:
                raise self.severe('Problem with "end-before" option of "%s" '
                                  'directive:\nText not found.' % self.name)
            rawtext = rawtext[:before_index]
        if 'literal' in self.options:
            # Convert tabs to spaces, if `tab_width` is positive.
            if tab_width >= 0:
                text = rawtext.expandtabs(tab_width)
            else:
                text = rawtext
            literal_block = nodes.literal_block(rawtext, text, source=path)
            literal_block.line = 1
            return [literal_block]
        else:
            include_lines = statemachine.string2lines(
                rawtext, tab_width, convert_whitespace=1)
            self.state_machine.insert_input(include_lines, path)
            return []


index = {
    'vimeo': Vimeo,
    'youtube': Youtube,
    'math': Math,
    'mathjax': MathJax,
    'code': Code,
    'sourcecode': SourceCode,
    'attachment-image': AttachmentImage,
    'attachment-figure': AttachmentFigure,
    'subpages': SubPages,
    'include-hg': IncludeHg,
    'include': IncludeHg,
}
