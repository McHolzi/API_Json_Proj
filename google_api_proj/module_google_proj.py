from __future__ import print_function
import requests
from key_origin_maps import key, origin, destination
from pprint import pprint
import datetime
from datetime import datetime
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from personal_data import trainer_name, address
import numpy as np
import json



def get_distance(origin, desitination):

    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={address}&destinations={destination}&departure_time=now&key={key}"

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.__dict__



def get_sheet_values(sheetname): 

    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

    ##### authentication #####
    creds = ServiceAccountCredentials.from_json_keyfile_name("google_api_proj\key_file.json", scope)
    client = gspread.authorize(creds)

    ##### get the data as a pandas Dataframe for readability #####
    sheet = client.open(sheetname).sheet1

    ##### add and delete rows ####
    '''
    row_to_add = ["the", "first", "change"]
    sheet.append_row(row_to_add)
    sheet.delete_rows(7)
    '''
    ####### get only specific columns or rows #####
    '''
    column_ranges = ['A:A', 'B:B']
    data = pd.DataFrame(sheet.batch_get(column_ranges)).transpose()
    '''
    #### gets all data #### 
    data_all = pd.DataFrame(sheet.get_all_records())

    #### looks at the relevant data ####
    data_relevant = data_all[data_all.columns[data_all.columns.isin(['Kursdatum','Ort','Datum', 'Date', 'Kursort','Trainer', 'Dauer (h)', 'Beginn'])]]

    free_courses = pd.DataFrame()
    my_courses = pd.DataFrame()

    #### checks for free courses and the courses already taken by me #### 
    free_courses = data_relevant[data_relevant['Trainer'] == ''] #When there is nothing in the Trainer column, the course is still free
    my_courses = data_relevant[data_relevant['Trainer'] == trainer_name] #When my Name is in the Trainer column its already taken by me

    return(free_courses, my_courses)


def clean_sheet_values(sheet_values):
    
    #### drops extra Rows, rename Dauer column ######
    i = sheet_values[(sheet_values.Ort == '')].index #index of the rows with no 'Ort' in them
    sheet_values = sheet_values.drop(i)              #drops the rows 
    sheet_values = sheet_values.reset_index(drop=True)
    sheet_values.rename(columns = {'Dauer (h)': 'Dauer'}, inplace = True)

    #### gets the dates with / in them, slices out the second Date, saves it in a list #### 
    temp_new_dates = sheet_values[(sheet_values.Kursdatum.str.contains('/'))] #takes out only the rows with '/' in the date
    replace_values = temp_new_dates.Kursdatum.str.slice(start=3, stop = 7)    #slices out the '/' and the Day of the date thats following
    replace_values_list = replace_values.values.tolist()                      # converts it to list 

    #### replaces the dates with the one before the / Delimiter (e.g. 11./12.10.2022 will be 11.10.2022), probably way more complicated then necessary ### 
    for i in range(len(replace_values_list)):
        temp_new_dates = temp_new_dates.replace(temp_new_dates.iloc[i]['Kursdatum'], temp_new_dates.Kursdatum.str.replace(replace_values_list[i], '').iloc[i])

    
    ##### split the dates with '/' in them, deletes the ones that are not complete (e.g. 10. which comes from splitting 10./11.10.2022), appends the full dates (e.g. 10.10.2022) #######
    sheet_values = sheet_values.assign(Kursdatum = sheet_values['Kursdatum'].str.split('/')).explode('Kursdatum') #splits the dates with '/' in them
    sheet_values = sheet_values.reset_index(drop = True)                                                          
    index_newdate = sheet_values[(~sheet_values.Kursdatum.str.contains('2022'))].index                            #index of the dates that are incomplete
    sheet_values = sheet_values.drop(index_newdate, axis=0)                                                       #drops the incomplete rows
    sheet_values = sheet_values.append(temp_new_dates)                                                            #appends the corresponding complete rows
    sheet_values = sheet_values.reset_index(drop=True)

    #### adds new column with datetime timestamp, adds new column with Endtime (Beginn + Dauer)#####
    format_time_before = '%d.%m.%Y/%H:%M:%S%z'
    sheet_values['Starttime'] = sheet_values['Kursdatum']+'/'+sheet_values['Beginn']+':00'+'+02:00'
    sheet_values['Starttime'] = sheet_values['Starttime'].apply(datetime.datetime.strptime, args= (format_time_before,))
    index_16h = sheet_values[(sheet_values.Dauer == 16)].index
    sheet_values.loc[index_16h, 'Dauer'] = 8
    index_6h = sheet_values[(sheet_values.Dauer == 6)].index
    sheet_values.loc[index_6h, 'Endtime'] = pd.to_datetime(sheet_values['Starttime'].astype(str)) + pd.DateOffset(hours = 6)
    index_8h = sheet_values[(sheet_values.Dauer == 8)].index
    sheet_values.loc[index_8h, 'Endtime'] = pd.to_datetime(sheet_values['Starttime'].astype(str)) + pd.DateOffset(hours = 8)

    return(sheet_values)

def get_creds_calendar():

       # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/calendar']


    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(r'C:\Users\Marco Holzer\API_Json_Proj\google_api_proj\token.json'):
        creds = Credentials.from_authorized_user_file(r'C:\Users\Marco Holzer\API_Json_Proj\google_api_proj\token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r'C:\Users\Marco Holzer\API_Json_Proj\google_api_proj\credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(r'C:\Users\Marco Holzer\API_Json_Proj\google_api_proj\token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def get_values_calendar(count):

    creds = get_creds_calendar()

    try:
        service = build('calendar', 'v3', credentials=creds)
        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print(f'Getting the upcoming {count} events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=count, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

    except HttpError as error:
        print('An error occurred: %s' % error)

    return events

def set_values_calendar(event):

    creds = get_creds_calendar()

    try:
        service = build('calendar', 'v3', credentials=creds)
        ''' event = {
    'summary': 'Google I/O 2015',
    'location': '800 Howard St., San Francisco, CA 94103',
    'description': 'A chance to hear more about Google\'s developer products.',
    'start': {
        'dateTime': '2022-05-28T09:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
    },
    'end': {
        'dateTime': '2022-05-28T17:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
    },

    'reminders': {
        'useDefault': False,
        'overrides': [
        {'method': 'email', 'minutes': 24 * 60},
        {'method': 'popup', 'minutes': 10},
        ],
    },
    }
        '''
        event = service.events().insert(calendarId='primary', body=event).execute()

    except HttpError as error:
        print('An error occurred: %s' % error)

def change_colour_events(event_count, colorid):

    creds = get_creds_calendar()
    events = get_values_calendar(event_count)

    for event in events:

        if 'colorId' in event and event['colorId'] != colorid and event['organizer'].get('displayName') == 'Schulung Burgenland':
            try:
                service = build('calendar', 'v3', credentials=creds)
                event['colorId'] = str(colorid)
                updated_event = service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
            
            except HttpError as error:
                print('An error occurred: %s' % error)

        if 'colorId' not in event and event['organizer'].get('displayName') == 'Schulung Burgenland':
            
            try:
                service = build('calendar', 'v3', credentials=creds)
                event['colorId'] = str(colorid)
                updated_event = service.events().update(calendarId='primary', eventId=event['id'], body=event).execute()
                print(event)
            except HttpError as error:
                print('An error occurred: %s' % error)

    return True

def get_values_maps(origin, destination):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&departure_time=now&key={key}"

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.text


def add_driving_time(event_count, organizer_name = 'Schulung Burgenland'):
    ####### reads the events and gets the starttime of the ones with the right Organizer
    ####### gets the location of the same events, and asks the maps api for the driving time (distance and stuff available as well)
    ####### adds the driving Time to the start time (needs to be changed, was just for troubleshooting)
    ####### needs to be written in a function
    events = get_values_calendar(event_count)

    format_time = '%Y-%m-%dT%H:%M:%S%z'
    event_last = {'summary' : ''}
    for event in events: 
        organizer = event['organizer'].get('displayName')
        check = 'Dauer' not in event_last['summary']

        if organizer == organizer_name and 'Dauer' not in event_last['summary']:
            buffer_time = datetime.timedelta(minutes = 20)
            starttime =  datetime.datetime.strptime(event['start'].get('dateTime'), format_time) 
            starttime_drive = starttime - buffer_time
            place = event['location']  
            distance = get_values_maps(address, place)
            dist_json = json.loads(distance)
            driving_time = datetime.timedelta(minutes = round(dist_json['rows'][0]['elements'][0]['duration']['value']/60))
            time_for_drive = starttime - driving_time - buffer_time
            print(organizer + ' in ' + place + ' Dauer:' + str(round(dist_json['rows'][0]['elements'][0]['duration']['value']/60)))

     ####### creates new event with the start and endtime calculated 
            event = {
                        'summary': '',
                        'description': 'Fahrt zum Kurs',
                        'start': {
                            'dateTime': '',
                        },
                        'end': {
                            'dateTime': '',
                        },
                        'colorId': '8',

                        }
            event['start']['dateTime'] = time_for_drive.strftime(format_time)
            event['end']['dateTime'] = starttime_drive.strftime(format_time)
            event['summary'] = 'Dauer: ' + str(driving_time)
            
            set_values_calendar(event)
            print('Fahrzeit hinzugefuegt')

        event_last = event
        

def compare_calendar_sheets(free_courses_sheets, events_calendar):

    event_df_final = pd.DataFrame(columns = ['Name', 'Starttime', 'Endtime', 'Organizer'])
    for event in events_calendar: 
        if event['start'].get('dateTime'):
            event_single = {

                'Name': [event['summary']],
                'Starttime': [event['start'].get('dateTime')],
                'Endtime': [event['end'].get('dateTime')],
                'Organizer': [event['organizer'].get('displayName')]
                }
        else: 
             event_single = {

                'Name': [event['summary']],
                'Starttime': [event['start'].get('date')],
                'Endtime': [event['end'].get('date')],
                'Organizer': [event['organizer'].get('displayName')]
                }

        event_df = pd.DataFrame(data = event_single)
        event_df_final = event_df_final.append(event_df)
    event_df_final = event_df_final.reset_index()
    event_df_final = event_df_final.drop(columns="index")
    event_df_final['Dauer'] = pd.to_datetime(event_df_final['Endtime']) - pd.to_datetime(event_df_final['Starttime'])

    return event_df_final
       
        