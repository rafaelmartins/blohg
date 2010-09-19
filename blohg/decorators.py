# -*- coding: utf-8 -*-

import re

from flask import current_app, request, abort
from functools import wraps

def validate_locale(f):
    @wraps(f)
    def new_f(*args, **kwargs):
        match = re.match(r'/([^/]+).*', request.path)
        if match is not None:
            locale = match.group(1)
            if locale not in current_app.config['LOCALES']:
                abort(404)
        return f(*args, **kwargs)
    return new_f
