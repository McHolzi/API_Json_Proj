import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
import pandas as pd
from personal_data import trainer_name


scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

##### authentication #####
creds = ServiceAccountCredentials.from_json_keyfile_name("google_api_proj\key_file.json", scope)
client = gspread.authorize(creds)

##### get the data as a pandas Dataframe for readability #####
sheet = client.open("test").sheet1

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