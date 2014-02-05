# coding: utf-8

from hashlib import md5
from calendar import timegm

from .single import Occurence
from upoutdf.duration import Duration

class OccurenceBlock(object):

    original_string = None
    every = None

    _occurences = []

    timezone = None
    type = None

    #Will be in UTC
    starting_date = None
    #Will be in timezone
    starting_date_infinite = None

    #Will be in UTC
    ending_date = None
    #Will be in timezone
    ending_date_infinite = None


    occurence_duration = None


    def __init__(self,starting_date,ending_date,
            starting_date_infinite,ending_date_infinite,
            typeobj):

        self._occurences = []
            
        self.starting_date = starting_date
        self.ending_date = ending_date

        self.starting_date_infinite = starting_date_infinite
        self.ending_date_infinite = ending_date_infinite

        self.original_string = typeobj.original_string
        self.every = typeobj.every
        self.timezone = typeobj.timezone
        self.type = typeobj.type


    def __hash__(self):
        list = []

        for o in self._occurences:
            #occurence hash returns md5, which is case insensitive
            list.append(o.__hash__())

        #lexicographical sorting
        h = " ".join(sorted(list, key=str.lower))
        h = "%s %s" % (h,self.timezone.zone)

        return md5(h).hexdigest()

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.__hash__() == other.__hash__() 

    def __ne__(self, other):
        return not self.__eq__(other)


    @property
    def localized_starting_date(self):
        if self.timezone is None or self.starting_date is None:
            return None

        return self.timezone.normalize(
            self.starting_date.astimezone(self.timezone)
        )

    @property
    def localized_ending_date(self):
        if self.timezone is None or self.ending_date is None:
            return None

        return self.timezone.normalize(
            self.ending_date.astimezone(self.timezone)
        )

    @property
    def unix_starting_date(self):
        #UTC
        return timegm(self.starting_date.utctimetuple())

    @property
    def unix_ending_date(self):
        #UTC
        return timegm(self.ending_date.utctimetuple())

    def get_occurences(self):
        #DO NOT CONVERT TO GENERATOR
        return self._occurences

    def add_occurence(self,start,end):
        self._occurences.append(Occurence(
            start=start,
            end=end,
            timezone=self.timezone
        ))

    def get_duration(self):
        return Duration(
            start = self.unix_starting_date,
            end = self.unix_ending_date
        )