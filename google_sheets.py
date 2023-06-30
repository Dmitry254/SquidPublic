import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = ""
spreadsheet_id = ""


def google_sheet_login():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)
    return service


def get_google_sheet_data(range_data):
    range_data = f"Squid!{range_data}"
    service = google_sheet_login()
    values = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_data
    ).execute()
    return values['values']


if __name__ == "__main__":
    bus_range_data = 'A3:B7'
    bus_data = get_google_sheet_data(bus_range_data)
    print(bus_data)
