# coding: utf-8

import pytz
from dateutil.relativedelta import relativedelta
from calendar import monthrange

from .tools import yearrange
from .dow import DATEUTIL_DOWS,DOWS

class BaseSnap(object):

    def __init__(self,timezone):
        self.timezone = timezone

    def _localized_datetime(self,datetime):
        return self.timezone.normalize(datetime.astimezone(self.timezone))

    def _to_utc(self,datetime):
        return pytz.utc.normalize(datetime.astimezone(pytz.utc))

    #Snaps date to nearest day of week in list
    def snap_to_dow(self,datetime,dows):
        raise NotImplementedError("Snapping class must implement snap_to_dow")

    #Snaps date to day of the month if possible
    def snap_to_month_day(self,datetime,day):
        raise NotImplementedError("Snapping class must implement snap_to_month_day")

    #Snaps date to month weekday (Xth friday for example) in list
    #Ordinal can either be an integer 1-5 or 'last'
    def snap_to_month_weekday(self,datetime,dows,ordinal):
        raise NotImplementedError("Snapping class must implement snap_to_month_day")



class SnapLogical(BaseSnap):
    """
    Implements 'logical' (at least, for our needs) snapping
    This will snap days of the week to the next closest day of week (could overflow month)
    It will snap the month day to the closest month day within that month (if possible, will never overflow month)
    """
    def snap_to_dow(self,datetime,dow):
        #Dow should be in ISO8601 formart
        localized = self._localized_datetime(datetime)
        
        localized_weekday = localized.isoweekday()

        distance = dow - localized_weekday

        if distance < 0:
            #Since its negative dont subtract
            distance = 7 + distance

        if distance != 0 and distance is not None:
            #relativedelta provides us better accuracy
            localized = localized + relativedelta(days=+distance)

        return self._to_utc(localized)

    def snap_to_month_day(self,datetime,day):
        localized = self._localized_datetime(datetime)

        month = monthrange(localized.year,localized.month)
        #month[1] = days in month
        #month[0] = weekday of first day of the month

        if day < 1 or day > month[1]:
            raise ValueError("Month day %s falls outside of range available for %s,%s (%s-%s)"
                %(day,localized.month,localized.year,month[0],month[1])
            )

        distance = day - localized.day
        #13 21 = -8, need to snap down 8 to the 13th
        #21 13 = 8, need to snap up 8 to 21

        #relativedelta provides us better accuracy
        if distance != 0:
            localized = localized + relativedelta(days=distance)

        return self._to_utc(localized)

    def snap_to_weekday_ordinal(self,datetime,dow,ordinal):
        localized = self._localized_datetime(datetime)

        if ordinal == 'last':
            if dow not in DATEUTIL_DOWS:
                raise ValueError("Invalid day of week %s, must be 1-7 (mon-sun)"%dow)

            #We need to ensure that this is the 1st of the month
            #Calling .replace here is not enough as it will not account for DST
            #Remember we are using LOCALIZED times here
            negative_delta = relativedelta(days=-localized.day+1)
            localized = localized + negative_delta
            #We're now at the first
            localized = localized + relativedelta(months=+1)
            #We're now at the first of the next month
            
            #If the first day of the month is the day we want, we need 2 weeks back
            if localized.isoweekday() == dow:
                last_delta = relativedelta(weekday=DATEUTIL_DOWS[dow](-2))
            else:
                last_delta = relativedelta(weekday=DATEUTIL_DOWS[dow](-1))

            #This will find the previous occurence of the dow
            #Since we're at the first of the next month,
            #this will be the last occurence in the previous month
            localized = localized + last_delta

            return self._to_utc(localized)

        else:
            try:
                ordinal = int(ordinal)
            except ValueError:
                raise ValueError("Ordinal must either be an integer 1-5 or 'last'")

            if ordinal < 1 or ordinal > 5:
                raise ValueError("Ordinal must either be an integer 1-5 or 'last'")

            #We need to ensure that this is the 1st of the month
            #Calling .replace here is not enough as it will not account for DST
            #Remember we are using LOCALIZED times here
            negative_delta = relativedelta(days=-localized.day+1)
            localized = localized + negative_delta

            localized_dow = localized.isoweekday()

            if localized_dow > dow:
                #Set to monday
                days = 8 - localized_dow
                localized = localized + relativedelta(days=+days)
                localized_dow = 1

            modifier = (ordinal - 1) * 7 + (dow - localized_dow)

            if modifier > 0:
                localized = localized + relativedelta(days=modifier)
                
            return self._to_utc(localized)


    def snap_to_year_day(self,datetime,yearday):
        localized = self._localized_datetime(datetime)

        year = yearrange(localized.year)

        if yearday < year[0] or yearday > year[1]:
            raise ValueError("Year day %s falls outside of range available for %s (%s-%s)"
                %(yearday,localized.year,year[0],year[1])
            )

        localized_yearday = localized.timetuple().tm_yday
        distance = yearday - localized_yearday
        # 200 201 = -1 needs to go down 1 to the 200th
        # 201 200 = 1 needs to go up 1 to the 201st

        if distance != 0:
            localized = localized + relativedelta(days=distance)

        return self._to_utc(localized)
        
