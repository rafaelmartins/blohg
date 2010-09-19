#!/usr/bin/env python
# -*- coding: utf-8 -*-

from blohg import create_app

#import os
#cwd = os.path.dirname(os.path.abspath(__file__))
#config_file = os.path.join(cwd, 'development.cfg')

app = create_app('/development/mercurial/rafaelmartins-blohg/config/development.py')
app.run(debug=True)
