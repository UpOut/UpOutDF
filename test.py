from upoutdf.parse import get_class


#test = "every month on last sunday,monday starting _October_15_2012_8:00PM ending _April_1_2014 at 8:00PM lasting 120 minutes in America/Los_Angeles"
#test = "every month day 4 starting _October_1_2013 ending _April_1_2014 at 8:00PM lasting 2 hours in America/Los_Angeles"

#test = "every weeks on tuesday,monday at 9:00PM lasting 6 hours in America/Los_Angeles"
test = "once starting _05/23/2015_08:00_PM ending _05/23/2015_11:00_PM in US/Pacific"
z = get_class(test)

def localize(time,timezone):
    return timezone.normalize(time.astimezone(timezone))

z.verify()
z.parse()


print z.canonicalize()

#print z.occurences().__hash__()

#print "FROM HERE"
#for block in z.occurences().get_blocks():
#    print block.__hash__()
#    for o in block.get_occurences():
 #       pass
        #print o.__hash__()

  #  print "\n\n"
    #start = localize(start,z.timezone)
    #end = localize(end,z.timezone)
    #print start
    #print start.isoweekday()
    #print end
    #print end.isoweekday()
    #print "\n\n---"



"""
from upoutdf.snapping import SnapLogical
from dateutil import parser
import pytz

tz = pytz.timezone('America/Los_Angeles')
date = parser.parse("February 5, 2014")
date = tz.localize(date)
date = pytz.utc.normalize(date.astimezone(pytz.utc))

snapper = SnapLogical(tz)

print snapper.snap_to_month_weekday(date,5,'last')
"""

"""
FORMATS:
    RECURRING:
        every (int) <year(s) (day <int>)| month(s) on <<1st,2nd,3rd,4th,5th,last> <m,t,w,tr,f,sa,s> | day <int>> | week(s) on <m,t,w,tr,f,sa,s> | day(s)> (starting <datetimestring>) (ending <datetimestring>) (repeating <int> times) at <timestamp> lasting <int> <hours,minutes,seconds> in <timezone>
    SINGLE:
        once starting <datetimestring> ending <datetimestring> in America/Los_Angeles

Both starting and ending are inclusive

every [int] [years/months/weeks/days] [day][on] [dow] [int] starting [date] ending [date] at [time] lasting[hours] 

every month on 3rd thursday at 9:00PM lasting 6 hours in America/Los_Angeles

3rd thursday of every month 
At 9:00pm until 3AM


every 1 year at TIMESTAMP lasting 4 hours in America/Los_Angeles

every week starting TIMESTAMP ending TIMESTAMP at TIMESTAMP until TIMESTAMP in America/New_York_City
"""