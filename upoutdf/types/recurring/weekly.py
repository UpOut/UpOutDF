# coding: utf-8

import pytz
from dateutil.relativedelta import relativedelta

from upoutdf import dow
from upoutdf.occurences import OccurenceBlock, OccurenceGroup
from .base import BaseRecurring
from upoutdf.constants import WEEKLY_TYPE

class WeeklyType(BaseRecurring):

    days_of_week = []

    required_attributes = [
        'every',
        'timezone',
        'starting_time',
        'lasting_seconds',
        'type',
        'days_of_week',
        'starting_date',
    ]

    def increment_by(self):
        return relativedelta(weeks=+self.every)
    
    def _snap_datetime(self,datetime,dow):
        if datetime is None:
            return None
        snapper = self.snapping_class(self.timezone)
        return snapper.snap_to_dow(datetime,dow)

    def _canonicalize_date(self,date):
        if not date.tzinfo:
            date = date.replace(tzinfo=pytz.utc)

        if date.tzinfo != self.timezone:
            date = self.timezone.normalize(date.astimezone(self.timezone))

        return date

    #_MM/dd/yyyy_h:mm_a
    def canonicalize(self):

        canonical = "every %s week" % self.every

        dows = []
        for d in self.days_of_week:
            dows.append(dow.DOWS[d])

        dows = ",".join(dows)

        canonical = "%s on %s" % (canonical,dows)
        #(starting <datetimestring>) (ending <datetimestring>)

        if not self.starting_date_infinite:
            starting_date = self._canonicalize_date(self.starting_date)
            canonical = "%s starting %s" % (
                canonical,
                starting_date.strftime("_%m/%d/%Y")
            )

        if not self.ending_date_infinite:
            ending_date = self._canonicalize_date(self.ending_date)
            canonical = "%s ending %s" % (
                canonical,
                ending_date.strftime("_%m/%d/%Y")
            )

        if self.repeating_count is not None:
            canonical = "%s repeating %s times" % (
                canonical,
                self.repeating_count
            )

        starting_time = self._canonicalize_date(self.starting_time)
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

        occurence_blocks = []

        for day in self.days_of_week:
            occurence_start = self._snap_datetime(self.starting_date,day)
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
            occurence_blocks.append(occurence_block)

        return OccurenceGroup(blocks=occurence_blocks)

    def _parse_type(self,tokens):

        if tokens[0] !='on':
            raise RuntimeError("Weekly type must specify 'on'")

        tokens = self._step_tokens(tokens)
        tokens[0] = tokens[0].strip(',')

        self.days_of_week = dow.determine_dows(tokens[0])

        tokens = self._step_tokens(tokens)

        #If the token after the next token is a day of the week, theres a problem
        is_dow = None
        try:
            is_dow = dow.determine_dows(tokens[0])
        except ValueError:
            pass

        if is_dow:
            raise ValueError("Days of week must not be seperated by spaces")

        self.type = WEEKLY_TYPE

        return tokens



