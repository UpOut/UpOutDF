# coding: utf-8

import pytz
from dateutil.relativedelta import relativedelta

from .base import BaseRecurring
from upoutdf.occurences import OccurenceBlock, OccurenceGroup
from upoutdf.constants import YEARLY_TYPE

class YearlyType(BaseRecurring):

    year_day = None

    required_attributes = [
        'every',
        'timezone',
        'starting_time',
        'lasting_seconds',
        'type',
        'starting_date'
    ]

    def increment_by(self):
        return relativedelta(years=+self.every)

    def _snap_datetime(self,datetime,yearday):
        if datetime is None:
            return None
        snapper = self.snapping_class(self.timezone)
        return snapper.snap_to_year_day(datetime,yearday)

    def canonicalize(self):

        canonical = "every %s year" % self.every
        
        if self.year_day is not None:
            canonical = "%s day %s" % (
                canonical,
                self.year_day
            )
        
        #(starting <datetimestring>) (ending <datetimestring>)

        if not self.starting_date_infinite:
            starting_date = self.timezone.normalize(self.starting_date.astimezone(self.timezone))
            canonical = "%s starting %s" % (
                canonical,
                starting_date.strftime("_%m/%d/%Y")
            )

        if not self.ending_date_infinite:
            ending_date = self.timezone.normalize(self.ending_date.astimezone(self.timezone))
            canonical = "%s ending %s" % (
                canonical,
                ending_date.strftime("_%m/%d/%Y")
            )

        if self.repeating_count is not None:
            canonical = "%s repeating %s times" % (
                canonical,
                self.repeating_count
            )

        starting_time = self.timezone.normalize(self.starting_time.astimezone(self.timezone))
        canonical = "%s at %s" % (
            canonical,
            starting_time.strftime("%-I:%M%p")
        )
        
        canonical = "%s lasting %s seconds in %s" % (
            canonical,
            self.lasting_seconds,
            str(self.timezone)
        )

        return canonical

    def occurences(self):
        if not self.verify_parsed():
            raise RuntimeError("Please call parse before calling occurences")

        ending = self.ending_date
        repeating_count = self.repeating_count

        ending_date_infinite = self.ending_date_infinite

        if repeating_count is not None:
            ending_date_infinite = False

        if ending is not None:
            ending = self._set_start_time(ending)
            ending = self._strip_microseconds(ending)

        occurence_start = self.starting_date
        if self.year_day is not None:
            try:
                occurence_start = self._snap_datetime(self.starting_date,self.year_day)
            except ValueError:
                #If we had a problem, try the next year
                occurence_start = self._snap_datetime(
                    self.starting_date+relativedelta(years=+1),
                    self.year_day
                )

        occurence_start = self._set_start_time(occurence_start)
        occurence_start = self._strip_microseconds(occurence_start)

        occurence_block = OccurenceBlock(
            starting_date=occurence_start,
            ending_date=None,
            starting_date_infinite=self.starting_date_infinite,
            ending_date_infinite=ending_date_infinite,
            typeobj=self
        )
        repeated = 1
        occurence_end = None
        #While we're before the end date (if we have it)
        #And we're before the max repetetions (if we have it)
        while ((ending is None or occurence_start <= ending) 
                and (repeating_count is None or repeated <= repeating_count)):

            occurence_end = self._get_end_datetime(occurence_start)
            occurence_end = self._strip_microseconds(occurence_end)
            
            occurence_block.add_occurence(occurence_start,occurence_end)

            occurence_start = self._increment_occurence(occurence_start)
            occurence_start = self._strip_microseconds(occurence_start)

            repeated+=1

        occurence_block.ending_date = occurence_end

        #We always return a OccurenceGroup, even if just 1
        return OccurenceGroup(blocks=[occurence_block])


    def _parse_type(self,tokens):

        if tokens[0] == 'day':
            tokens = self._step_tokens(tokens)
            
            try:
                self.year_day = int(tokens[0])
            except ValueError:
                raise ValueError("Invalid year day")
            
            tokens = self._step_tokens(tokens)

        self.type = YEARLY_TYPE
        
        return tokens



