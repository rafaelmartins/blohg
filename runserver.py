#!/usr/bin/env python
# -*- coding: utf-8 -*-

from blohg import create_app

import os
cwd = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(cwd, 'development.cfg')

app = create_app(config_file)

del app.config['GOOGLE_ANALYTICS']
app.config['DISQUS_DEVELOPER'] = True

app.run(debug=True)
