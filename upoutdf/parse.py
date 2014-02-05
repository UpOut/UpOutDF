# coding: utf-8

from dateutil import parser
from .types.recurring import get_type_class
from .types.single import SingleType

def get_class(toparse,
        date_parsing_function=None):

    tokens = toparse.split()

    every_int = 1

    if tokens[0] == 'every':

        tokens=tokens[1:]
        try:
            every_int = int(tokens[0])
            tokens = tokens[1:]
        except ValueError: 
            every_int = 1

        type_class = get_type_class(tokens)
        tokens = tokens[1:]

        return type_class(
            original_string=toparse,
            tokens=tokens,
            every=every_int,
            date_parse=date_parsing_function
        )

    elif tokens[0] == 'once':

        tokens=tokens[1:]
        
        return SingleType(
            original_string=toparse,
            tokens=tokens,
            date_parse=date_parsing_function
        )

    raise ValueError("Could not determine token class type, must be 'once' or 'every'")
