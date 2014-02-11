# coding: utf-8

from datetime import datetime

import pytz
from dateutil import parser
from dateutil.relativedelta import relativedelta

from upoutdf.snapping import SnapLogical
from ..base import BaseType

class BaseRecurring(BaseType):

    original_string = None
    
    type = None
    required_attributes = []

    every = 1
    timezone = None

    #Repeating range
    starting_date_infinite = True
    starting_date = None

    ending_date_infinite = True
    ending_date = None

    repeating_count = None

    #time
    lasting_seconds = None
    starting_time = None

    def __init__(self,original_string,tokens,every,
            date_parse=None,
            default_ending_interval=None,
            snapping_class=None):

        self.original_string = original_string
        self.tokens = tokens
        self.every = every

        if date_parse is None:
            date_parse = parser.parse

        if default_ending_interval is None:
            default_ending_interval = relativedelta(years=3)

        if snapping_class == None:
            snapping_class = SnapLogical

        self.date_parse = date_parse
        self.default_ending_interval = default_ending_interval
        self.snapping_class = snapping_class

    def verify(self):
        try:
            self.parse()
            self.occurences()
        except:
            return False
        
        return True

    """ OCCURENCE TOOLS """
    def _strip_microseconds(self,datetime):
        return datetime - relativedelta(microseconds=datetime.microsecond)

    def increment_by(self):
        raise NotImplementedError("increment_by() not implemented")

    #Increment to the next occruence
    def _increment_occurence(self,datetime):
        datetime = self.timezone.normalize(datetime.astimezone(self.timezone))
        datetime = datetime + self.increment_by()
        datetime = pytz.utc.normalize(datetime.astimezone(pytz.utc))
        #Don't trust relative delta to keep the same times in every case
        #We want to ensure the times are kept across DST for example
        return self._set_start_time(datetime)

    #Set a datetime to the same time specified in starting_time
    def _set_start_time(self,datetime):
        #This may be required to handle DST
        datetime = self.timezone.normalize(datetime.astimezone(self.timezone))
        starting_time = self.timezone.normalize(self.starting_time.astimezone(self.timezone))

        datetime = datetime.replace(
            hour=starting_time.hour,
            minute=starting_time.minute,
            second=starting_time.second
        )

        return pytz.utc.normalize(datetime.astimezone(pytz.utc))

    #Add the duration to get the ending datetime for a starting datetime
    def _get_end_datetime(self,datetime):
        datetime = self.timezone.normalize(datetime.astimezone(self.timezone))
        datetime = datetime + relativedelta(seconds=+self.lasting_seconds)
        return pytz.utc.normalize(datetime.astimezone(pytz.utc))

    def occurences(self):
        raise NotImplementedError("Each recurring type must implement the occurences method")

    def _set_default_period(self,timezone):
        #We always need a start date
        if self.starting_date is None:
            self.starting_date = datetime.utcnow().replace(tzinfo=pytz.utc)
            self.starting_date = timezone.normalize(self.starting_date.astimezone(timezone))

        if self.repeating_count is None:
            #Only default if we dont have repeating
            if self.ending_date is None:
                #Default to 3 years in the future
                self.ending_date = datetime.utcnow().replace(tzinfo=pytz.utc)
                self.ending_date = self.ending_date + self.default_ending_interval

                self.ending_date = timezone.normalize(self.ending_date.astimezone(timezone))


    def _step_tokens(self,tokens):
        tokens = tokens[1:]
        return tokens

    def verify_parsed(self):
        if self.ending_date is None and self.repeating_count is None:
            return False

        for attr in self.required_attributes:
            try:
                if not getattr(self,attr):
                    return False
            except AttributeError:
                return False

        return True

    def parse(self):

        try:

            if self.tokens[-2:-1][0] != "in":
                raise ValueError("Missing timezone token 'in'")

            self.timezone = pytz.timezone(self.tokens[-1:][0])

            tokens = self._parse_type(self.tokens)

            #Default the border types first
            self.ending_date_infinite = True
            self.starting_date_infinite = True

            tokens = self._parse_period(tokens,self.timezone)
            
            self._set_default_period(self.timezone)

            tokens = self._parse_time(tokens,self.timezone)

            return True
            
        except IndexError:
            raise ValueError("Incomplete date string passed")
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError("Unknown timezone specified")

        return False

    def _parse_time(self,tokens,timezone):
        if tokens[0] != 'at':
            raise ValueError("Missing time token 'at'")

        tokens = self._step_tokens(tokens)

        #if first character underscore, treat all underscores as spaces
        if tokens[0][0] == '_':
            tokens[0] = tokens[0].replace("_"," ").strip()

        #Get time
        try:
            time = self.date_parse(tokens[0])
        except:
            raise ValueError("Unable to parse start time")

        time = timezone.localize(time)
        self.starting_time = pytz.utc.normalize(time.astimezone(pytz.utc))

        tokens = self._step_tokens(tokens)

        if tokens[0] !='lasting':
            raise ValueError("Missing lasting token 'lasting'")

        tokens = self._step_tokens(tokens)

        #Get lasting
        try:
            lasting = int(tokens[0])
        except ValueError: 
            raise ValueError("Unable to read lasting token, a positive non-zero integer is required")

        if lasting <= 0:
            raise ValueError("Unable to read lasting token, a positive non-zero integer is required")

        tokens = self._step_tokens(tokens)

        #convert to seconds
        if tokens[0] == 'hours':
            lasting = lasting * 60 * 60
        elif tokens[0] == 'minutes':
            lasting = lasting * 60
        elif tokens[0] == 'seconds':
            lasting = lasting
        else:
            raise ValueError("Lasting not labeled as hours, minutes or seconds")

        self.lasting_seconds = lasting

        return tokens


    def _parse_period(self,tokens,timezone):
        if tokens[0] == 'starting':
            tokens = self._step_tokens(tokens)

            #if first character underscore, treat all underscores as spaces
            if tokens[0][0] == '_':
                tokens[0] = tokens[0].replace("_"," ").strip()

            try:
                starting = self.date_parse(tokens[0])
            except:
                raise ValueError("Unable to parse starting date string")

            starting = timezone.localize(starting)
            self.starting_date = pytz.utc.normalize(starting.astimezone(pytz.utc))
            self.starting_date_infinite = False

            return self._parse_period(self._step_tokens(tokens),timezone)

        elif tokens[0] == 'ending':
            tokens = self._step_tokens(tokens)

            #if first character underscore, treat all underscores as spaces
            if tokens[0][0] == '_':
                tokens[0] = tokens[0].replace("_"," ").strip()

            try:
                ending = self.date_parse(tokens[0])
            except:
                raise ValueError("Unable to parse ending date string")

            ending = timezone.localize(ending)
            self.ending_date = pytz.utc.normalize(ending.astimezone(pytz.utc))
            self.ending_date_infinite = False

            return self._parse_period(self._step_tokens(tokens),timezone)

        elif tokens[0] == 'repeating':
            tokens = self._step_tokens(tokens)

            try:
                self.repeating_count = int(tokens[0])
            except ValueError: 
                raise ValueError("Token after repeating must be a positive non-zero integer")

            if self.repeating_count < 1:
                self.repeating_count = None
                raise ValueError("Token after repeating must be a positive non-zero integer")

            tokens = self._step_tokens(tokens)

            if tokens[0] != 'times':
                raise ValueError("Missing repeating token seperator 'times'")

            return self._parse_period(self._step_tokens(tokens),timezone)

        return tokens

    def _parse_type(self,tokens):
        raise NotImplementedError("Each recurring type must implement the _parse_type method")