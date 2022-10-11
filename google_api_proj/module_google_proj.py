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
from personal_data import trainer_name
import numpy as np




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

    #### drops extra Rows, rename Dauer column ######
    i = free_courses[(free_courses.Ort == '')].index #index of the rows with no 'Ort' in them
    free_courses = free_courses.drop(i)              #drops the rows 
    free_courses = free_courses.reset_index(drop=True)
    free_courses.rename(columns = {'Dauer (h)': 'Dauer'}, inplace = True)

    #### gets the dates with / in them, slices out the second Date, saves it in a list #### 
    temp_new_dates = free_courses[(free_courses.Kursdatum.str.contains('/'))] #takes out only the rows with '/' in the date
    replace_values = temp_new_dates.Kursdatum.str.slice(start=3, stop = 7)    #slices out the '/' and the Day of the date thats following
    replace_values_list = replace_values.values.tolist()                      # converts it to list 

    #### replaces the dates with the one before the / Delimiter (e.g. 11./12.10.2022 will be 11.10.2022), probably way more complicated then necessary ### 
    for i in range(len(replace_values_list)):
        temp_new_dates = temp_new_dates.replace(temp_new_dates.iloc[i]['Kursdatum'], temp_new_dates.Kursdatum.str.replace(replace_values_list[i], '').iloc[i])

    
    ##### split the dates with '/' in them, deletes the ones that are not complete (e.g. 10. which comes from splitting 10./11.10.2022), appends the full dates (e.g. 10.10.2022) #######
    free_courses = free_courses.assign(Kursdatum = free_courses['Kursdatum'].str.split('/')).explode('Kursdatum') #splits the dates with '/' in them
    free_courses = free_courses.reset_index(drop = True)                                                          
    index_newdate = free_courses[(~free_courses.Kursdatum.str.contains('2022'))].index                            #index of the dates that are incomplete
    free_courses = free_courses.drop(index_newdate, axis=0)                                                       #drops the incomplete rows
    free_courses = free_courses.append(temp_new_dates)                                                            #appends the corresponding complete rows
    free_courses = free_courses.reset_index(drop=True)

    #### adds new column with datetime timestamp #####
    free_courses['Datetime'] = free_courses['Kursdatum']+'/'+free_courses['Beginn']+':00'+'+02:00'
    free_courses['Datetime'] = pd.to_datetime(free_courses['Datetime'])
    index_16 = free_courses[(free_courses.Dauer == 16)].index
    free_courses.loc[index_16, 'Dauer'] = 8
    


    return(free_courses)


def get_values_calendar(count):

    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/calendar']


    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('google_api_proj/token.json'):
        creds = Credentials.from_authorized_user_file('google_api_proj/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'google_api_proj/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('google_api_proj/token.json', 'w') as token:
            token.write(creds.to_json())

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

     # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/calendar']


    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('google_api_proj/token.json'):
        creds = Credentials.from_authorized_user_file('google_api_proj/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'google_api_proj/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('google_api_proj/token.json', 'w') as token:
            token.write(creds.to_json())

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


def get_values_maps(origin, destination):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&departure_time=now&key={key}"

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.text

