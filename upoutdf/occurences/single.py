# coding: utf-8

from hashlib import md5
from calendar import timegm
from math import ceil

from upoutdf.duration import Duration

class Occurence(object):

    #Will be UTC
    start = None
    end = None

    timezone = None

    def __init__(self,start,end,timezone):
        self.start = start
        self.end = end

        self.timezone = timezone

    def __hash__(self):
        #Why use cryptographic hashes?
        #We want this to be compatible across systems.
        #I should be able to store these hashes in a DB for comparison
        #I also want to avoid going out of stdlib for now

        #REMEMBER MD5'S ARE CASE INSENSITIVE, WE HAVE .lower TO ENSURE CONSISTENCY
        return md5("%s %s %s %s %s"  % (
            self.timezone.zone,
            self.unix_start,
            self.unix_end,
            self.start.microsecond,
            self.end.microsecond
        )).hexdigest().lower()

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self.__hash__() == other.__hash__()

    def __ne__(self, other):
        return not self.__eq__(other)

    def _day_second(self,datetime):
        return (datetime.hour * 60 * 60) + (datetime.minute * 60) + datetime.second

    def _week_second(self,datetime):
        weekday = datetime.isoweekday()

        #604800 seconds in a week (604799 is sunday, 23:59:59)
        #86400 seconds in a day
        #3600 seconds in an hour
        #60 seconds in a minute
        #1 second in a second LOLZ!

        return ((weekday - 1) * 86400) + (datetime.hour * 3600) + (datetime.minute * 60) + datetime.second;
    
    def _week_of_month(self,datetime):

        first = datetime.replace(day=1)

        adjusted_dom = datetime.day + (first.isoweekday() - 1)

        return int(ceil(adjusted_dom/7.0))


    @property
    def localized_start(self):
        return self.timezone.normalize(self.start.astimezone(self.timezone))

    @property
    def localized_end(self):
        return self.timezone.normalize(self.end.astimezone(self.timezone))

    @property
    def unix_start(self):
        #UTC
        return timegm(self.start.utctimetuple())

    @property
    def unix_end(self):
        #UTC
        return timegm(self.end.utctimetuple())

    def start_day_second(self,localized=False):
        
        start = self.start
        if localized:
            start = self.localized_start

        return self._day_second(start)

    def end_day_second(self,localized=False):
        
        end = self.end
        if localized:
            end = self.localized_end

        return self._day_second(end)

    def start_week_second(self,localized=False):
        
        start = self.start
        if localized:
            start = self.localized_start

        return self._week_second(start)

    def end_week_second(self,localized=False):
        
        end = self.end
        if localized:
            end = self.localized_end

        return self._week_second(end)

    def start_week_of_month(self,localized=False):
        
        start = self.start
        if localized:
            start = self.localized_start

        return self._week_of_month(start)

    def end_week_of_month(self,localized=False):
        
        end = self.end
        if localized:
            end = self.localized_end

        return self._week_of_month(end)

    def get_duration(self):
        return Duration(
            start = self.unix_start,
            end = self.unix_end
        )

