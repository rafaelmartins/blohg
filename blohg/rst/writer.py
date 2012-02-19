# -*- coding: utf-8 -*-
"""
    blohg.rst.writer
    ~~~~~~~~~~~~~~~~

    Module with the custom blohg reStructuredText HTML writer.

    :copyright: (c) 2010-2011 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from docutils.writers.html4css1 import HTMLTranslator, Writer

import re


class BlohgWriter(Writer):

    def __init__(self):
        Writer.__init__(self)
        self.translator_class = BlohgHTMLTranslator


class BlohgHTMLTranslator(HTMLTranslator):

    def visit_iframe_flash_video(self, node):
        atts = dict(src=node['uri'])
        if 'width' in node:
            atts['width'] = node['width']
        if 'height' in node:
            atts['height'] = node['height']
        if 'border' in node:
            atts['frameborder'] = node['border']
        if 'allowfullscreen' in node and node['allowfullscreen'] == 'true':
            # weird behavior of <iframe>, I'm not sure if this thing actually
            # works at all
            atts['allowfullscreen'] = 'true'
        style = []
        for att_name in 'width', 'height':
            if att_name in atts:
                if re.match(r'^[0-9.]+$', atts[att_name]):
                    # Interpret unitless values as pixels.
                    atts[att_name] += 'px'
                style.append('%s: %s;' % (att_name, atts[att_name]))
                del atts[att_name]
        if style:
            atts['style'] = ' '.join(style)
        if 'align' in node:
            atts['class'] = 'align-%s' % node['align']
        self.context.append('')
        self.body.append(self.starttag(node, 'iframe', '', **atts) + \
                         '</iframe>\n')

    def depart_iframe_flash_video(self, node):
        self.body.append(self.context.pop())
