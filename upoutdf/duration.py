# coding: utf-8

import math

class Duration(object):

    #Should be unix timestamps in UTC
    start = None
    end = None

    def __init__(self,start,end):
        self.start = start
        self.end = end

    @property
    def seconds(self):
        return self.end - self.start

    @property
    def minutes(self):
        minutes = self.seconds / 60.0
        #We round down as half a minute isnt a minute
        return math.floor(minutes)

    @property
    def hours(self):
        hours = self.minutes / 60.0
        #We round down as half an hour isnt an hour
        return math.floor(hours)

    @property
    def days(self):
        days = self.hours / 24.0
        #We round down as half a day isnt a day
        return math.floor(days)

    @property
    def weeks(self):
        weeks = self.days / 7.0
        #We round down as half a week isnt a week
        return math.floor(weeks)
