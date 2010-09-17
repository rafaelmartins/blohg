# -*- coding: utf-8 -*-

from docutils.core import publish_parts
from docutils.parsers.rst.directives import register_directive
import rst_directives

# registering docutils' directives
for directive in rst_directives.__directives__:
    register_directive(directive, rst_directives.__directives__[directive])


class RstParser(object):
    
    def __init__(self, metadata):
        self.metadata = metadata
    
    def _parse(self, content):
        parts = publish_parts(
            source = content,
            writer_name = 'html',
            settings_overrides = {
                'input_encoding': 'utf-8',
                'output_encoding': 'utf-8',
                'doctitle_xform': 0,
                'initial_header_level': 3,
            }
        )
        return parts['body']
    
    def parse(self):
        return self._parse(self.metadata.full)
    
    def parse_abstract(self):
        return self._parse(self.metadata.abstract)
