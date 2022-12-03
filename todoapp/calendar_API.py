from decouple import config
from google.oauth2 import service_account
import googleapiclient.discovery
import datetime
import json


CAL_ID = "104a92a3cd198c2062645e570737318d05c2dfb2f1361e64b743a4b0e223de66@group.calendar.google.com"
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = json.load(open('google-credentials.json'))


def test_calendar():
    print("RUNNING TEST_CALENDAR()")
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = googleapiclient.discovery.build(
        'calendar', 'v3', credentials=credentials)

    print(service)
    # CREATE A NEW EVENT
    new_event = {
        'summary': "New Task 1",
        'location': 'Kolkata, WB',
        'description': 'Description of Task 1',
        'start': {
            'date': f"{datetime.date.today()}",
            'timeZone': 'America/New_York',
        },
        'end': {
            'date': f"{datetime.date.today() + datetime.timedelta(days=3)}",
            'timeZone': 'America/New_York',
        },
    }
    service.events().insert(calendarId=CAL_ID, body=new_event).execute()
    print('Event created')

 # GET ALL EXISTING EVENTS
    events_result = service.events().list(
        calendarId=CAL_ID, maxResults=2500).execute()
    events = events_result.get('items', [])

    # LOG THEM ALL OUT IN DEV TOOLS CONSOLE
    for e in events:

        print(e)

    # uncomment the following lines to delete each existing item in the calendar
    #event_id = e['id']
        # service.events().delete(calendarId=CAL_ID, eventId=event_id).execute()

    return events
