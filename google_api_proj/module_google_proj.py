import requests
from key_origin_maps import key, origin, destination



def get_distance(origin, desitinations):

    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&departure_time=now&key={key}"

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.text



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
    free_courses = free_courses.append(data_relevant[data_relevant['Trainer'] == '']) #When there is nothing in the Trainer column, the course is still free
    my_courses = my_courses.append(data_relevant[data_relevant['Trainer'] == trainer_name]) #When my Name is in the Trainer column its already taken by me

    pprint(free_courses)

def get_values_calendar():

    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


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
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

    except HttpError as error:
        print('An error occurred: %s' % error)

    return events
