# -*- coding: utf-8 -*-
"""
    blohg.rst_directives
    ~~~~~~~~~~~~~~~~~~~~
    
    Module with the custom blohg reStructuredText directives.
    
    :copyright: (c) 2010-2011 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from docutils import nodes
from docutils.parsers.rst import directives, Directive
from docutils.parsers.rst.directives.images import Image, Figure
from flask import current_app, request, url_for
from urllib import pathname2url

import posixpath


__all__ = ['Youtube', 'Math', 'Code', 'AttachmentImage', 'AttachmentFigure',
           'SubPages']

GOOGLETEX_URL = 'https://chart.googleapis.com/chart?cht=tx&chl='


def align(argument):
    return directives.choice(argument, ('left', 'center', 'right'))


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
    final_argument_whitespace = True
    option_spec = {
        'height': directives.nonnegative_int,
        'width': directives.nonnegative_int,
        'align': align,
    }
    has_content = False

    def run(self):
        self.options['vid'] = self.arguments[0]
        if not 'width' in self.options:
            self.options['width'] = 425
        if not 'height' in self.options:
            self.options['height'] = 344
        if not 'align' in self.options:
            self.options['align'] = 'center'
        html = '''\

<div align="%(align)s">
<object width="%(width)i" height="%(height)i">
    <param name="movie" value="http://www.youtube.com/v/%(vid)s?fs=1&color1=0x3a3a3a&color2=0x999999"></param>
    <param name="allowFullScreen" value="true"></param>
    <param name="allowscriptaccess" value="always"></param>
    <embed src="http://www.youtube.com/v/%(vid)s?fs=1&color1=0x3a3a3a&color2=0x999999"
           type="application/x-shockwave-flash"
           allowscriptaccess="always"
           allowfullscreen="true"
           width="%(width)i"
           height="%(height)i">
    </embed>
</object>
</div>

'''
        return [nodes.raw('', html % self.options, format='html')]


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
        self.options['brush'] = self.arguments[0]
        html = '''\

<pre class="brush: %s">
%s
</pre>

'''
        return [nodes.raw('', html % (self.options['brush'],
            "\n".join(self.content).replace('<', '&lt;')),
            format='html')]


class Math(Image):
    """reStructuredText directive that creates an image HTML object to
    display a LaTeX equation, using Google Chart API.
    
    Usage example::
    
        .. math::
            
            \frac{x^2}{1+x}
    """
    
    required_arguments = 0
    has_content = True

    def run(self):
        if not 'align' in self.options:
            self.options['align'] = 'center'
        tmp = pathname2url(' '.join([(i == '' and '\\\\' or i.strip()) \
            for i in self.content]))
        self.arguments.append('%s%s' % (GOOGLETEX_URL, tmp))
        return Image.run(self)


class AttachmentImage(Image):
    
    def run(self):
        my_file = directives.uri(self.arguments[0])
        full_path = posixpath.join(current_app.config['ATTACHMENT_DIR'], my_file)
        if full_path not in list(current_app.hg.revision):
            raise self.error(
                'Error in "%s" directive: File not found: %s.' % (
                    self.name, full_path
                )
            )
        self.arguments[0] = url_for('.attachments', filename=my_file, _external=True)
        return Image.run(self)

    
class AttachmentFigure(Figure):
    
    def run(self):
        my_file = directives.uri(self.arguments[0])
        full_path = posixpath.join(current_app.config['ATTACHMENT_DIR'], my_file)
        if full_path not in list(current_app.hg.revision):
            raise self.error(
                'Error in "%s" directive: File not found: %s.' % (
                    self.name, full_path
                )
            )
        self.arguments[0] = url_for('.attachments', filename=my_file, _external=True)
        return Figure.run(self)


class SubPages(Directive):
    """reStructuredText directive that creates a bullet-list with the subpages of
    the current page, or of a given page.
    
    Usage example::

        .. subpages::
    
    Or::
    
        .. subpages:: projects
    
    Supposing that you have a directory called ``content/projects`` and some
    reStructuredText files on it. Subdirectories are also allowed.
    
    This directive will just show the files from the root of the directory. It's
    not recursive.
    """
    
    required_arguments = 0
    optional_arguments = 1
    has_content = False
    
    def _compare_by_slug(self, x, y):
        if x.slug > y.slug:
            return 1
        if x.slug < y.slug:
            return -1
        return 0
    
    def run(self):
        if len(self.arguments) == 0:
            self.arguments.append(request.path.strip('/'))
        tmp_metadata = []
        final_metadata = []
        # not sure if this works on windows
        splited_dir = self.arguments[0].split('/')
        for metadata in current_app.hg.get_all():
            # not sure if this works on windows
            splited_slug = metadata.slug.split('/')
            if metadata.slug.startswith(self.arguments[0]) and \
               (len(splited_dir) + 1 == len(splited_slug)):
                tmp_metadata.append(metadata)
        for metadata in sorted(tmp_metadata, self._compare_by_slug):
            link = url_for('views.content', slug=metadata.slug)
            reference = nodes.reference(link, metadata.title, refuri=link)
            final_metadata.append(nodes.list_item('', nodes.paragraph('', '', reference)))
        return [nodes.bullet_list('', *final_metadata)]
    

__directives__ = {
    'youtube': Youtube,
    'math': Math,
    'code': Code,
    'attachment-image': AttachmentImage,
    'attachment-figure': AttachmentFigure,
    'subpages': SubPages,
}
