from datetime import datetime, date
import time

# Returns Unix timestamp from day-month string. Ex 15/10
def getUnixTimestamp(stringDate):
    splitted = stringDate.split('/')
    year = date.today().year

    # Python date from imput
    pyDate = datetime(year, int(splitted[1]), int(splitted[0]), 10, 00)

    # Unix timestamp from date
    return time.mktime(pyDate.timetuple())