# -*- coding: utf-8 -*-
"""
    blohg.rst.writer
    ~~~~~~~~~~~~~~~~

    Module with the custom blohg reStructuredText HTML writer.

    :copyright: (c) 2010-2012 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

from docutils.writers.html4css1 import HTMLTranslator, Writer

import re


class BlohgWriter(Writer):

    def __init__(self):
        Writer.__init__(self)
        self.translator_class = BlohgHTMLTranslator

    def assemble_parts(self):
        # we will add 2 new parts to the writer: 'first_paragraph_as_text' and
        # 'images'
        Writer.assemble_parts(self)
        self.parts['first_paragraph_as_text'] = \
            self.visitor.first_paragraph_as_text
        self.parts['images'] = self.visitor.images


class BlohgHTMLTranslator(HTMLTranslator):

    def __init__(self, document):
        HTMLTranslator.__init__(self, document)
        self.first_paragraph_as_text = None
        self.images = []

    def visit_iframe_flash_video(self, node):
        if 'thumbnail_uri' in node:
            self.images.append(node['thumbnail_uri'])
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
        self.body.append(self.starttag(node, 'iframe', '', **atts) + \
                         '</iframe>\n')

    def depart_iframe_flash_video(self, node):
        pass

    def visit_paragraph(self, node):
        if self.first_paragraph_as_text is None:
            # just paragraphs at the root of the document should be used.
            # warnings, blockquotes and similar aren't good descriptions.
            if node.parent.tagname.strip() == 'document':
                self.first_paragraph_as_text = \
                    ' '.join([i.strip() \
                              for i in node.astext().splitlines(False)])
        HTMLTranslator.visit_paragraph(self, node)

    def visit_image(self, node):
        # opengraph specs allows multiple images.
        # http://ogp.me/#array
        self.images.append(node['uri'])
        HTMLTranslator.visit_image(self, node)
