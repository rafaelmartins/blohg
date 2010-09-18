# -*- coding: utf-8 -*-

import re

from flask import Flask, request
from flaskext.babel import Babel, lazy_gettext as _
from flaskext.themes import setup_themes, render_theme_template

from mercurial_content import MercurialContent
from rst_parser import RstParser

app = Flask('blohg')
app.config.setdefault('REPO_PATH', '/development/mercurial/rafaelmartins.eng.br')
app.config.setdefault('LOCALES', {'en-us': 'en_US'})

babel = Babel(app)
setup_themes(app)
hg = MercurialContent(app)

@babel.localeselector
def get_locale():
    match = re.match(r'/([^/]+).*', request.path)
    if match is not None:
        locale = match.group(1)
        if locale is not None:
            return app.config['LOCALES'].get(locale, None)

@app.route('/')
def home():
    return render_theme_template(
        'basic', 'index.html',
        variable = RstParser(hg.get('en-us', 'about')).parse()
    )


if __name__ == '__main__':
    app.run(debug = True)
