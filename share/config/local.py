# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from production import *

del GOOGLE_ANALYTICS
DEBUG = True
DISQUS_DEVELOPER = True
