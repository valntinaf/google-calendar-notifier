from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import notify2
import os

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

PATH = '/opt/google-calendar-notifier'

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    os.environ['DBUS_SESSION_BUS_ADDRESS']='unix:path=/run/user/1000/bus'

    if os.path.exists(PATH+'/token.pickle'):
        with open(PATH+'/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                PATH+'/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(PATH+'/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    calendarlist = service.calendarList().list(maxResults=10).execute()

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() +'Z' # 'Z' indicates UTC time

    notify2.init('notifier')

    for calendar in calendarlist['items']:
        calendar_id = calendar['id']
        print("Searching events for "+calendar['summary'])

        events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                            maxResults=3, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            if event['start'].get('dateTime',False):
                event_date = datetime.datetime.fromisoformat(event['start']['dateTime'])
                now_date = datetime.datetime.now()
                event_date = event_date.replace(tzinfo=None)
                difference = (event_date - now_date)
                minutes = difference.total_seconds() / 360
                if(minutes <= 1.5 and minutes > 0):
                    n = notify2.Notification(event['summary'],
                         calendar['summary'],
                         "/usr/share/icons/Honor/scalable/apps/gnome-calendar.svg"   # Icon name
                        )
                    n.show()

if __name__ == '__main__':
    main()
