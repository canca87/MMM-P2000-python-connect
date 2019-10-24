#import stuff to handle the JSON response data:
import json 
import urllib.request
#import stuff to handle the generation of URL API signatures:
from hashlib import sha1
import hmac
import binascii
#import stuff to handle the UTC -> Local time conversion:
from datetime import datetime
from dateutil import tz
#import stuff for the loop handling
import time

#some static data/variables for the script:
train_stop_ID = 1105  #your station ID
train_direction_ID = 1 #going towards the city... 7 would be away (depending on station information)
train_result_count = 3 #number of next trains to collect info for (3 next departures here...)
tram_stop_ID = -1#3252  #your station ID: set to -1 for bypassing - there are no trams near me.
tram_route_ID = 947 #trams and busses require a route, as multiple services run from the stops.
tram_direction_ID = 2 #going towards the city... 28 would be away (depending on station information)
tram_result_count = 3 #number of next trams to collect info for (3 next departures here...)
bus_stop_ID = 12977  #your stop ID
bus_route_ID = 950 #the bus route ID - from Swagger, as this is not the ID displayed on the bus!
bus_direction_ID = 217 #direction is known from Swagger
bus_result_count = 2 #number of next buses to collect info for (3 next departures here...)

#this function appends the request data to the URL and applied the correct signature to the end of it:
def getURL(request):
    #this is the devid and api key given to me by PTV
    #email APIKeyRequest@ptv.vic.gov.au to get a new one...
    devid = 1234567
    key = 'you-need-a-key-to-access'
    #check the request has a question mark in it, else apply one. otherwise just an '&' will do...
    request = request + ( '&' if ('?' in request) else '?')
    #attach my devid raw to the string:
    raw = request + 'devid={0}'.format(devid)
    #hash this with my key to generate the correct signature:
    hashed = hmac.new(key.encode('utf-8'),raw.encode('utf-8'),sha1)
    signature = hashed.hexdigest()
    #return the compiled URL:
    returnStr = 'https://timetableapi.ptv.vic.gov.au' + raw + '&signature={0}'.format(signature)
    return returnStr

def utc2local(utc_time_string):
    # METHOD 1: Hardcode zones:
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Australia/Melbourne')
    utc = datetime.strptime(utc_time_string, '%Y-%m-%dT%H:%M:%SZ')
    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    utc = utc.replace(tzinfo=from_zone)
    # Convert time zone
    aest = utc.astimezone(to_zone)
    # Return the string of the time (24-hour time only is enough. to the minute.)
    return aest.strftime('%H:%M')


def timeUntilUTC(utc_time_string):
    utc = datetime.strptime(utc_time_string, '%Y-%m-%dT%H:%M:%SZ')
    nowTime_aest = datetime.now()
    # METHOD 1: Hardcode zones:
    to_zone = tz.gettz('UTC')
    from_zone = tz.gettz('Australia/Melbourne')
    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    nowTime_aest = nowTime_aest.replace(tzinfo=from_zone)
    utc = utc.replace(tzinfo=to_zone)
    # Convert time zone
    nowTime_utc = nowTime_aest.astimezone(to_zone)
    time_diff = round((utc - nowTime_utc).seconds / 60,0)
    if time_diff > 1000:
        return 0
    else:
        return round(time_diff)


def getTrainExpressStatus(runID):
    # This URL returns whether this run is express, and also how many stops (counts) are bypassed express:
    #url_darebin_express = "http://timetableapi.ptv.vic.gov.au/v3/runs/21397/route_type/0?devid=1234567&signature=HEXSTRINGHERE"
    url_darebin_express = getURL('/v3/runs/{0}/route_type/0?'.format(runID))
    #grab the express data from the PTV
    with urllib.request.urlopen(url_darebin_express) as url:
        express_data = json.loads(url.read().decode())

    if express_data['run']['express_stop_count'] == 0:
        return 'All stations'
    else:
        return 'Express'


def getTrainCurrentDisruptionInfo(disruptionID):
    # This URL returns the disrution status of the Darebin line (planned and current)
    #url_darebin_disruptions = "https://timetableapi.ptv.vic.gov.au/v3/disruptions/166511?devid=1234567&signature=HEXSTRINGHERE"
    url_darebin_disruptions = getURL('/v3/disruptions/{0}?'.format(disruptionID))
    #grab the express data from the PTV
    with urllib.request.urlopen(url_darebin_disruptions) as url:
        disruption_data = json.loads(url.read().decode())

    if disruption_data['disruption']['disruption_status'] == "Current":
        return disruption_data['disruption']['description']
    else:
        return None

# This is going to be fairly rudimentary - Get the data in a fixed order:
if train_stop_ID >= 0:
    # This URL is used to get the next 3 departures from a train station
    url_train_departures = getURL('/v3/departures/route_type/0/stop/{0}?direction_id={1}&max_results={2}'.format(train_stop_ID,train_direction_ID,train_result_count))

    #grab the departures data from the PTV
    with urllib.request.urlopen(url_train_departures) as url:
        departure_data = json.loads(url.read().decode())
    #for each departure:
    print("Trains to city:")
    for departure in departure_data["departures"]:
        #get the departure time (comes in UTC string format):
        scheduled_departure_time_utc = departure["scheduled_departure_utc"]
        sched_time_local = (utc2local(scheduled_departure_time_utc))

        #get the info on the number of express stations (or stops all stations)
        express_status = (getTrainExpressStatus(departure['run_id']))

        #get the estimated time (comes in UTC string format):
        if departure["estimated_departure_utc"] == None:
            depating_in_minutes = ('Estimated in {0} min.'.format(timeUntilUTC(departure['scheduled_departure_utc'])))
        else:
            depating_in_minutes = ('Departing in {0} min.'.format(timeUntilUTC(departure['estimated_departure_utc'])))
        print("<br>{0} - {1} - {2}".format(sched_time_local,express_status,depating_in_minutes))

if tram_stop_ID >= 0:
    # This URL is used to get the next 3 departures from a train station
    url_tram_departures = getURL('/v3/departures/route_type/1/stop/{0}?direction_id={1}&max_results={2}'.format(tram_stop_ID,tram_direction_ID,tram_result_count))

    #grab the departures data from the PTV
    with urllib.request.urlopen(url_tram_departures) as url:
        departure_data = json.loads(url.read().decode())
    #for each departure:
    if train_stop_ID >= 0: #check if a new line char is needed before the header
        print("<br>")
    print("Trams to city:")
    for departure in departure_data["departures"]:
        #get the departure time (comes in UTC string format):
        scheduled_departure_time_utc = departure["scheduled_departure_utc"]
        sched_time_local = (utc2local(scheduled_departure_time_utc))

        #get the estimated time (comes in UTC string format):
        if departure["estimated_departure_utc"] == None:
            depating_in_minutes = ('Estimated in {0} min.'.format(timeUntilUTC(departure['scheduled_departure_utc'])))
        else:
            depating_in_minutes = ('Departing in {0} min.'.format(timeUntilUTC(departure['estimated_departure_utc'])))
        print("<br>{0} - {1}".format(sched_time_local,depating_in_minutes))

if bus_stop_ID >= 0:
    # This URL is used to get the next 3 departures from a train station
    url_bus_departures = getURL('/v3/departures/route_type/2/stop/{0}/route/{1}?direction_id={2}&max_results={3}'.format(bus_stop_ID,bus_route_ID,bus_direction_ID,bus_result_count))

    #grab the departures data from the PTV
    with urllib.request.urlopen(url_bus_departures) as url:
        departure_data = json.loads(url.read().decode())
    #for each departure:
    if train_stop_ID >= 0 or tram_stop_ID >= 0: #check if a new line char is needed before the header
        print("<br>")
    print("Bus to city:")
    for departure in departure_data["departures"]:
        #get the departure time (comes in UTC string format):
        scheduled_departure_time_utc = departure["scheduled_departure_utc"]
        sched_time_local = (utc2local(scheduled_departure_time_utc))

        #get the estimated time (comes in UTC string format):
        if departure["estimated_departure_utc"] == None:
            depating_in_minutes = ('Estimated in {0} min.'.format(timeUntilUTC(departure['scheduled_departure_utc'])))
        else:
            depating_in_minutes = ('Departing in {0} min.'.format(timeUntilUTC(departure['estimated_departure_utc'])))
        print("<br>{0} - {1}".format(sched_time_local,depating_in_minutes))
