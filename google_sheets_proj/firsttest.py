import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("google_sheets_proj\key_file.json", scope)
client = gspread.authorize(creds)

sheet = client.open("test").sheet1
#row_to_add = ["the", "first", "change"]
#sheet.append_row(row_to_add)
#sheet.delete_rows(7)

data = sheet.get_all_records()
pprint(data)