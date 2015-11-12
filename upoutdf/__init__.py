# coding: utf-8

__version__ = "0.7"

"""
This module uses the Gregorian calendar (over ISO8601) for all calculations.
This is for several reasons, but the 2 main ones are:
1. We want years to start on Jan 1
2. Python defaults Gregorian

HOWEVER we use ISO8601 notation for weekdays (1 = monday, 7 = sunday)

REQUIREMENTS:
python-dateutil http://labix.org/python-dateutil
pytz http://pytz.sourceforge.net/
"""