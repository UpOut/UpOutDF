# coding: utf-8

import pytz
from dateutil import parser

from .base import BaseType
from upoutdf.constants import SINGLE_TYPE
from upoutdf.occurences import OccurenceBlock, OccurenceGroup

class SingleType(BaseType):
    
    every = 1

    original_string = None
    
    timezone = None

    #Can never be infinite for single type
    starting_date_infinite = False
    ending_date_infinite = False

    starting_date = None
    ending_date = None

    def __init__(self,original_string,tokens,date_parse=None):
        if date_parse is None:
            date_parse = parser.parse

        self.original_string = original_string
        self.tokens = tokens
        self.date_parse = date_parse

    def verify(self):
        try:
            self.parse()
            self.occurences()
        except:
            return False
        
        return True
        
    def _step_tokens(self,tokens):
        tokens = tokens[1:]
        return tokens

    #_MM/dd/yyyy_h:mm_a
    def canonicalize(self):
        starting_date = self.timezone.normalize(self.starting_date.astimezone(self.timezone))
        ending_date = self.timezone.normalize(self.ending_date.astimezone(self.timezone))
        return "once starting %s ending %s in %s" % (
            starting_date.strftime("_%m/%d/%Y_%I:%M_%p"),
            ending_date.strftime("_%m/%d/%Y_%I:%M_%p"),
            str(self.timezone)
        )

    def occurences(self):
        occurence = OccurenceBlock(
            starting_date=self.starting_date,
            ending_date=self.ending_date,
            starting_date_infinite=self.starting_date_infinite,
            ending_date_infinite=self.ending_date_infinite,
            typeobj=self
        )
        occurence.add_occurence(self.starting_date,self.ending_date)

        #We ALWAYS must return a OccurenceGroup
        return OccurenceGroup(blocks=[occurence])

    def parse(self):

        try:

            if self.tokens[-2:-1][0] != "in":
                raise ValueError("Missing timezone token 'in'")

            self.timezone = pytz.timezone(self.tokens[-1:][0])

            #Handle starting time
            tokens = self.tokens
            if tokens[0] != 'starting':
                raise ValueError("Missing starting token 'starting'")

            tokens = self._step_tokens(tokens)

            if tokens[0][0] == '_':
                tokens[0] = tokens[0].replace("_"," ").strip()

            try:
                starting = self.date_parse(tokens[0])
            except:
                raise ValueError("Unable to parse starting date string")

            starting = self.timezone.localize(starting)
            self.starting_date = pytz.utc.normalize(starting.astimezone(pytz.utc))

            #Handle ending time
            tokens = self._step_tokens(tokens)
            if tokens[0] != 'ending':
                raise ValueError("Missing ending token 'ending'")

            tokens = self._step_tokens(tokens)

            if tokens[0][0] == '_':
                tokens[0] = tokens[0].replace("_"," ").strip()

            try:
                ending = self.date_parse(tokens[0])
            except:
                raise ValueError("Unable to parse ending date string")

            ending = self.timezone.localize(ending)
            self.ending_date = pytz.utc.normalize(ending.astimezone(pytz.utc))

            self.type = SINGLE_TYPE
            
            return True
            
        except IndexError:
            raise ValueError("Incomplete date string passed")
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError("Unknown timezone specified")

        return False

