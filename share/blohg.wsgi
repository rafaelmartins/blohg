# -*- coding: utf-8 -*-
"""
    blohg.wsgi
    ~~~~~~~~~~

    Example WSGI script for Apache/mod_wsgi.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import os
os.environ['HGENCODING'] = 'utf-8'

# If you're using virtualenv, uncomment the code below
#import site
#site.addsitedir('/path/to/your/virtualenv/lib/pythonX.Y/site-packages')

from blohg import create_app
application = create_app('/path/to/your/repo',
    ## Uncomment the line below to enable embedded extensions
    #embedded_extensions=True
)
