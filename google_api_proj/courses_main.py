import module_google_proj as mgp
from pprint import pprint
import json
from personal_data import address
import datetime

def main():

    #sheetval = mgp.get_sheet_values('test')
    #print(sheetval)

    events = mgp.get_values_calendar(10)


    ####### reads the events and gets the starttime of the ones with the right Organizer
    ####### gets the location of the same events, and asks the maps api for the driving time (distance and stuff available as well)
    ####### adds the driving Time to the start time (needs to be changed, was just for troubleshooting)
    ####### needs to be written in a function
    format_time = '%Y-%m-%dT%H:%M:%S%z'
    for event in events: 
        organizer = event['organizer'].get('displayName')
        if organizer == 'Schulung Burgenland':
            starttime =  datetime.datetime.strptime(event['start'].get('dateTime'), format_time)
            place = event['location']  
            distance = mgp.get_values_maps(address, place)
            dist_json = json.loads(distance)
            driving_time = datetime.timedelta(minutes = round(dist_json['rows'][0]['elements'][0]['duration']['value']/60))
            time_after_drive = starttime + driving_time
            print(organizer + 'in ' + place + ' Dauer:' + str(round(dist_json['rows'][0]['elements'][0]['duration']['value']/60)))



    ####### creates new event with the start and endtime calculated 
    event = {
                'summary': 'Fahrt',
                'description': 'Fahrt zum Kurs',
                'start': {
                    'dateTime': '',
                },
                'end': {
                    'dateTime': '',
                },

                }
    event['start']['dateTime'] = starttime.strftime(format_time)
    event['end']['dateTime'] = time_after_drive.strftime(format_time)
    mgp.set_values_calendar(event)
        
            

if __name__ == "__main__":
    main()