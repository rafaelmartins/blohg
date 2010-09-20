# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from remote import *

try:
    del GOOGLE_ANALYTICS
except:
    pass
DEBUG = True
DISQUS_DEVELOPER = True
