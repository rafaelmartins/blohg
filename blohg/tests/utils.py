# -*- coding: utf-8 -*-
"""
    blohg.tests.utils
    ~~~~~~~~~~~~~~~~~

    Module with tests for blohg utilities.

    :copyright: (c) 2010-2013 by Rafael Goncalves Martins
    :license: GPL-2, see LICENSE for more details.
"""

import unittest

from blohg.utils import parse_date


class UtilsTestCase(unittest.TestCase):

    def test_parse_date(self):
        # 1234567890 == 2009-02-13 23:31:30
        from_ts = parse_date('1234567890')
        from_str = parse_date('2009-02-13 23:31:30')
        self.assertTrue(isinstance(from_ts, int), 'parsed ts is not an int')
        self.assertTrue(isinstance(from_str, int), 'parsed str is not an int')
        self.assertEqual(from_ts, from_str)
