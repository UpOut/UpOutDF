==========
UpOut DateFormat Parser
==========

About
==========

This is a parser for the UpOut DateFormat. This format is designed to be easily readable by python humans and machines.
You can see more details about the format below.

While this library is ready for use, it needs to be cleaned up quite a bit. We also need better format documentation and unit tests


Usage
==========
from upoutdf.parse import get_class

container = get_class("upout dateformat string")

#Will return True/False to denote any issues
#Not required to get occurences
container.verify()

#Will raise an exception if there is a problem, ValueError or RuntimeError
#Will return False if there was an unknown issue
#MUST be called before .occurences() below
container.parse()

#Will get a list of upoutdf.occurences.OccurenceBlock objects
occurences = container.occurences()

for block in ocurrences:
	#Will get list of UTC datetime tuples, including the start and end of each occurence
	#Can also use get_localized_occurences to get the occurences localized to the timezone
	for start,end in occurences.get_occurences()

	

Format
==========
FORMATS:
    RECURRING:
        every (int) <year(s) (day <int>)| month(s) on <<1st,2nd,3rd,4th,5th,last> <m,t,w,tr,f,sa,s> | day <int>> | week(s) on <m,t,w,tr,f,sa,s> | day(s)> (starting <datetimestring>) (ending <datetimestring>) (repeating <int> times) at <timestamp> lasting <int> <hours,minutes,seconds> in <timezone>
    SINGLE:
        once starting <datetimestring> ending <datetimestring> in America/Los_Angeles

Both starting and ending are inclusive
If any of the <datetimestring> objects begins with _ then all _ in that object will be converted to spaces
We tokenize based on spaces

Example:
every week on monday,tuesday at 9:00PM lasting 6 hours in America/Los_Angeles

every month on last saturday,monday starting _October_1_2013 ending _April_1_2014 at 8:00PM lasting 2 hours in America/Los_Angeles
once starting _October_1_2013_5:00_PM ending _March_1_2014_5:00_PM in America/Los_Angeles

TODO
==========
Better format documentation
Unit tests
Cleanup classes
