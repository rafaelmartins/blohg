# -*- coding: utf-8 -*-
"""
    blohg.views.robots
    ~~~~~~~~~~~~~~~~~~
    
    View module that deals with the robots.txt generation.
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: BSD, see LICENSE for more details.
"""

from flask import Module, make_response, render_template

robots = Module(__name__)


@robots.route('/robots.txt')
def robots_txt():
    """The robots.txt view."""
    response = make_response(render_template('robots.txt'))
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response
