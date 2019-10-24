# MMM-PTV
Inspired by the MMM-P2000-python-connect module, I modified it for displaying train/bus/tram
information from PTV (Public Transport Victoria, Australia). The API developer code and key 
are required in order to access the real-time timetable and scheduling information.

I am using the same python management as the P2000-python-connect module on a 30 second refresh
schedule. The python script returns a html formatted string, containing all the data I needed.

The python script can show train, bus and tram schedules, and is programmed specific to my needs.
First, I use the Swagger UI interface with my developer keys to determine the route, stop, direction
 and route type information I need. The swagger interface can be accessed here:
 http://timetableapi.ptv.vic.gov.au/swagger/ui/index

 You can request new API keys by following the instructions under the "Registering for an API key" section:
 https://www.ptv.vic.gov.au/footer/data-and-reporting/datasets/ptv-timetable-api/


The Files includes a python project based on:
https://nl.oneguyoneblog.com/2016/08/09/p2000-ontvangen-decoderen-raspberry-pi/#comment-488

