from upoutdf.parse import get_class


#test = "every week on monday,tuesday at 9:00PM lasting 6 hours in America/Los_Angeles"
test = "once starting _October_1_2013_5:00PM ending _October_1_2013_9:30PM in America/Los_Angeles"
z = get_class(test)

def localize(time,timezone):
    return timezone.normalize(time.astimezone(timezone))

print z.verify()
z.parse()


#z.occurences()

print "FROM HERE"
for block in z.occurences():
    print block
    for start,end in block.get_occurences():

        print localize(start,z.timezone)
        print localize(end,z.timezone)
        print "\n"

    print "\n\n"
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