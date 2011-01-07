# -*- coding: utf-8 -*-
"""
    blohg.functions
    ~~~~~~~~~~~~~~~
    
    Helper functions for Jinja2 templates.
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import re
from flask import current_app, request, url_for


def my_locale():
    match = re.match(r'/([^/]+).*', request.path)
    if match is not None:
        return match.group(1)
    return 'en-us'


def current_path():
    match = re.match(r'/[^/]+/(.+)/', request.path)
    if match is not None:
        return match.group(1)
    return ''


def active_page():
    return current_path().split('/')[0]


def i18n_config(key):
    config = current_app.config.get(key, None)
    if config is None:
        return None
    locale = current_app.config['LOCALES'][my_locale()]['locale']
    if locale in config:
        return config[locale]
    if type(config) == dict:
        values = config.values()
        if len(values) > 0:
            return config.values()[0]
        return None
    return config


def i18n_url_for(endpoint, **kwargs):
    if 'locale' not in kwargs:
        kwargs['locale'] = my_locale()
    return url_for(endpoint, **kwargs)
