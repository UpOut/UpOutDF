# coding: utf-8


class OccurenceBlock(object):

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

        self.timezone = typeobj.timezone
        self.type = typeobj.type

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

    def get_occurences(self):
        #DO NOT CONVERT TO GENERATOR
        return self._occurences

    def get_localized_occurences(self):
        #DO NOT CONVERT TO GENERATOR
        localized = []

        for start,end in self._occurences:
            l_start = self.timezone.normalize(start.astimezone(self.timezone))
            l_end = self.timezone.normalize(end.astimezone(self.timezone))
            localized.append((l_start,l_end))

        return localized


    def add_occurence(self,start,end):
        self._occurences.append((start,end))