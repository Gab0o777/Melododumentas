from datetime import datetime, date
from exceptions import InvalidParamsFormatException, InvalidArgumentNumberException
import time

# Returns Unix timestamp from day-month string. Ex 15/10
def getUnixTimestamp(stringDate):
    splitted = stringDate.split('/')
    year = date.today().year

    # Python date from imput
    pyDate = datetime(year, int(splitted[1]), int(splitted[0]), 10, 00)

    # Unix timestamp from date
    return time.mktime(pyDate.timetuple())

def isValidDate(date1):
    dayMonth = date1.split("/")

    if isinstance(int(dayMonth[0]), int) and isinstance(int(dayMonth[1]), int):
        return True
    
    return False

def validateDates(dateString):
    datesSplit = dateString.split(" ")

    if len(datesSplit) != 2:
        raise Exception(InvalidArgumentNumberException)
    
    # if (not isValidDate(datesSplit[0]) or not isValidDate(datesSplit[1])):
    #     raise Exception(InvalidParamsFormatException)


