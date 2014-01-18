# coding: utf-8

import pytz
from dateutil.relativedelta import relativedelta

from .base import BaseRecurring
from upoutdf.occurences import OccurenceBlock
from upoutdf.constants import DAILY_TYPE

class DailyType(BaseRecurring):

    required_attributes = [
        'every',
        'timezone',
        'starting_time',
        'lasting_seconds',
        'type',
        'starting_date'
    ]

    def increment_by(self):
        return relativedelta(days=+self.every)

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

        #We always return a list, even if just 1
        return [occurence_block]


    def _parse_type(self,tokens):

        self.type = DAILY_TYPE
        
        return tokens



