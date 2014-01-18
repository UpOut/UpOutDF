# coding: utf-8

from upoutdf import constants

from .daily import DailyType
from .weekly import WeeklyType
from .monthly import MonthlyType
from .yearly import YearlyType

import re

_PRE_RE_TYPES = (
    r'(da(ys?|il(y|ies)))|(^d$)',
    r'(week(s|l(y|ies))?)|(^w$)',
    r'(month(s|l(y|ies))?)|(^m$)',
    r'year(s|l(y|ies))?|(^y$)'
)

DEFAULT_RE_TYPES = [re.compile(r) for r in _PRE_RE_TYPES]

DEFAULT_TYPE_CLASSMAP = [
    DailyType,
    WeeklyType,
    MonthlyType,
    YearlyType
]

def get_type_class(tokens,
        regex_types=None,regex_type_classmap=None,
        keep_default_types=True,keep_default_classmap=True):

    if not regex_types:
        regex_types = DEFAULT_RE_TYPES
    else:
        if keep_default_types:
            regex_types = regex_types + DEFAULT_RE_TYPES

    if not regex_type_classmap:
        regex_type_classmap = DEFAULT_TYPE_CLASSMAP
    else:
        if keep_default_classmap:
            regex_type_classmap = regex_type_classmap + DEFAULT_TYPE_CLASSMAP

    matched = []

    for i, type in enumerate(regex_types):
        if type.search(tokens[0]):
            try:
                matched.append(regex_type_classmap[i])    
            except IndexError:
                raise RuntimeError("Could not find class for type %s" % tokens[0])

    if not matched:
        raise ValueError("Invalid type %s" % tokens[0])

    if len(matched) > 1:
        raise ValueError("Type %s too ambiguous" % tokens[0])

    return matched[0]



