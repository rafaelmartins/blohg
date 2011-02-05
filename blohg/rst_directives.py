# -*- coding: utf-8 -*-
"""
    blohg.rst_directives
    ~~~~~~~~~~~~~~~~~~~~
    
    Module with the custom blohg reStructuredText directives.
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from docutils import nodes
from docutils.parsers.rst import directives, Directive
from docutils.parsers.rst.directives.images import Image
from urllib import pathname2url

__all__ = ['Youtube', 'Math', 'Code']

# temporary mimetex url
MIMETEX_URL = 'http://pidsim.rafaelmartins.eng.br/cgi-bin/mimetex.cgi'


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
    display a LaTeX equation, using Mimetex.
    
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
        self.arguments.append('%s?%s' % (MIMETEX_URL, tmp))
        return Image.run(self)


__directives__ = {
    'youtube': Youtube,
    'math': Math,
    'code': Code,
}
