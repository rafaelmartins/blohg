# -*- coding: utf-8 -*-
"""
    blohg.decorators
    ~~~~~~~~~~~~~~~~
    
    Module with some decorators for the blohg views.
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: BSD, see LICENSE for more details.
"""

import re
from flask import current_app, request, abort
from functools import wraps


def validate_locale(f):
    """Simple decorator that checks if the `request.path` contains a
    proper locale. If not, raises a 404 error.
    
    :param f: the decorated view function.
    """
    
    @wraps(f)
    def new_f(*args, **kwargs):
        match = re.match(r'/([^/]+).*', request.path)
        if match is not None:
            locale = match.group(1)
            if locale not in current_app.config['LOCALES']:
                abort(404)
        return f(*args, **kwargs)
    return new_f
