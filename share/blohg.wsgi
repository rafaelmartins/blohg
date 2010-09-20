# -*- coding: utf-8 -*-
"""
    blohg.wsgi
    ~~~~~~~~~~
    
    Example WSGI script for Apache/mod_wsgi.
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: BSD, see LICENSE for more details.
"""

# If you're using virtualenv, uncomment the code below
#import site
#site.addsitedir('/path/to/your/virtualenv/lib/pythonX.Y/site-packages')

from blohg import create_app
application = create_app('/path/to/your/repo/config/remote.py')
