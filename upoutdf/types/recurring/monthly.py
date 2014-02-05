# coding: utf-8

import pytz
from dateutil.relativedelta import relativedelta

from upoutdf import dow
from .base import BaseRecurring
from upoutdf.occurences import OccurenceBlock, OccurenceGroup
from upoutdf.constants import MONTHLY_MONTHDAY_TYPE, MONTHLY_WEEKDAY_TYPE

class MonthlyType(BaseRecurring):

    month_weekdays = []
    month_weekday_number = None
    month_weekday_last = None

    month_day = None

    required_attributes = [
        'every',
        'timezone',
        'starting_time',
        'lasting_seconds',
        'type',
        'starting_date'
    ]

    def increment_by(self):
        return relativedelta(months=+self.every)

    def _snap_monthday_datetime(self,datetime,monthday):
        if datetime is None:
            return None
        snapper = self.snapping_class(self.timezone)
        return snapper.snap_to_month_day(datetime,monthday)

    #Snap to month weekday (1st,2nd,3rd,4th,5th,last) (m,t,w,tr,f,sa,s)
    def _snap_weekday_ordinal_datetime(self,datetime,dow,ordinal):
        if datetime is None:
            return None
        snapper = self.snapping_class(self.timezone)
        #We dont want to allow month overflow
        original_month = snapper._localized_datetime(datetime).month

        snapped = snapper.snap_to_weekday_ordinal(datetime,dow,ordinal)

        #If we overflow, snap to next increment that has this ordinal
        localized = snapper._localized_datetime(snapped)
        
        while localized.month != original_month:
            datetime = self._increment_occurence(datetime)
            original_month = snapper._localized_datetime(datetime).month

            snapped = snapper.snap_to_weekday_ordinal(datetime,dow,ordinal)
            localized = snapper._localized_datetime(snapped)

        return snapped

    def _weekday_occurences(self):
        
        ordinal = None
        if self.month_weekday_last:
            ordinal = 'last'
        elif self.month_weekday_number is not None:
            ordinal = self.month_weekday_number

        if ordinal is None:
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

        for day in self.month_weekdays:
            occurence_start = self._snap_weekday_ordinal_datetime(self.starting_date,day,ordinal)
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
                #We need to snap after increment as well
                occurence_start = self._snap_weekday_ordinal_datetime(occurence_start,day,ordinal)
                #Since we're snapping lets be sure about times
                occurence_start = self._set_start_time(occurence_start)
                occurence_start = self._strip_microseconds(occurence_start)
                
                repeated+=1

            occurence_block.ending_date = occurence_end
            occurence_blocks.append(occurence_block)

        return OccurenceGroup(blocks=occurence_blocks)


    def _monthday_occurences(self):
        
        ending = self.ending_date
        repeating_count = self.repeating_count

        ending_date_infinite = self.ending_date_infinite

        if repeating_count is not None:
            ending_date_infinite = False

        if ending is not None:
            ending = self._set_start_time(ending)
            ending = self._strip_microseconds(ending)

        occurence_start = self.starting_date

        occurence_start = self._snap_monthday_datetime(occurence_start,self.month_day)
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



    def occurences(self):
        if not self.verify_parsed():
            raise RuntimeError("Please call parse before calling occurences")

        if self.type == MONTHLY_WEEKDAY_TYPE:
            if not self.month_weekdays:
                raise RuntimeError("Please call parse before calling occurences")
            
            if not self.month_weekday_number and not self.month_weekday_last:
                raise RuntimeError("Please call parse before calling occurences")

            return self._weekday_occurences()

        elif self.type == MONTHLY_MONTHDAY_TYPE:
            if not self.month_day:
                raise RuntimeError("Please call parse before calling occurences")

            return self._monthday_occurences()

        raise RuntimeError("Please call parse before calling occurences")

    def _parse_type(self,tokens):

        if tokens[0] == 'on':
            tokens = self._step_tokens(tokens)

            if tokens[0] == 'last':
                self.month_weekday_last = True
                self.month_weekday_number = None
                tokens = self._step_tokens(tokens)
            else:
                self.month_weekday_last = False
                try:
                    #First character will always be int like 1st,2nd,3rd,4th,5th
                    self.month_weekday_number = int(tokens[0][0])
                except ValueError:
                    raise ValueError("Invalid month weekday number, can be 1st,2nd,3rd,4th,5th or last")

                if self.month_weekday_number < 1 or self.month_weekday_number > 5:
                    raise ValueError("Invalid month weekday number, can be 1st,2nd,3rd,4th,5th or last")

                tokens = self._step_tokens(tokens)

            #Determine day of week
            self.month_weekdays = dow.determine_dows(tokens[0])
            tokens = self._step_tokens(tokens)

            #If the token after the next token is a day of the week, theres a problem
            is_dow = None
            try:
                is_dow = dow.determine_dows(tokens[0])
            except ValueError:
                pass

            if is_dow:
                raise ValueError("Days of week must not be seperated by spaces")


            self.type = MONTHLY_WEEKDAY_TYPE

        elif tokens[0] == 'day':
            tokens = self._step_tokens(tokens)

            try:
                self.month_day = int(tokens[0])
            except ValueError:
                raise ValueError("Month day token must be followed by an integer between 1-31")

            if self.month_day < 1 or self.month_day > 31:
                self.month_day = None
                raise ValueError("Month day token must be followed by an integer between 1-31")   

            tokens = self._step_tokens(tokens)
            self.type = MONTHLY_MONTHDAY_TYPE          

        else:
            raise ValueError("Month type must be followed by 'on' or 'day' tokens")
        
        return tokens



