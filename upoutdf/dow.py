# coding: utf-8

import re
from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU

#Monday is 1, Sunday is 7
#Meant to line up with ISO8601
#http://en.wikipedia.org/wiki/ISO_8601
#http://docs.python.org/2/library/datetime.html#datetime.date.isoweekday

DOWS = {
    1:'monday',
    2:'tuesday',
    3:'wednesday',
    4:'thursday',
    5:'friday',
    6:'saturday',
    7:'sunday'
}

DATEUTIL_DOWS = {
    1:MO,
    2:TU,
    3:WE,
    4:TH,
    5:FR,
    6:SA,
    7:SU
}

_PRE_RE_DOWS = (
    r'(mon?(day)s?)|(^m$)',
    r'(tue?s?(days?))|(^t$)',
    r'(we(dnes|nds|ns|des|d)day)|(^w$)',
    r'(th(urs|ers)day)|(th((u|r)|ur)?s?)|(tr)|(^r$)',
    r'(fri?(day))|(^f$)',
    r'(sat?([ue]rday))|(sa)|(^s$)',
    r'(sun?(day))|(sn)|(^u$)',
    r'weekdays?',
    r'weekends?'
)

#DoW values mapped to the same indicies as which regex expression above represents them
_DOW_MAP = [
    [1],[2],[3],[4],[5],[6],[7],
    [1,2,3,4,5],
    [6,7]
]
_RE_DOWS = [re.compile(r) for r in _PRE_RE_DOWS]

def determine_dows(string):
    if "," in string:
        strings = string.split(",")
    else:
        strings = [string]

    found = []
    for s in strings:
        was_found = False
        for i, dow in enumerate(_RE_DOWS):
            if dow.search(s):
                found += _DOW_MAP[i]
                was_found = True
                break

        if not was_found:
            raise ValueError("Invalid day of week %s in string %s" % (s,string))

    if not found:
        raise ValueError("Unable to find valid day of week in "+string)

    #convert to set to eliminate duplicates
    #convert back for compatibility
    return list(set(found))

