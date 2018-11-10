import datetime
import requests
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

class CalendarReader():

    def __init__(self,
                 cred_path,
                 token_file='token.json',
                 credentials_file='credentials.json'):
        self.scopes = 'https://www.googleapis.com/auth/calendar.readonly'
        creds = self.get_credentials(cred_path, token_file, credentials_file)
        self.calendar = build('calendar', 'v3', http=creds.authorize(Http()))
        #self.device_id_map = self.get_device_id_map()

    def get_credentials(self, cred_path, token_file, credentials_file):
        '''Run authorization procedure. Use valid access token if it exists;
           otherwise, use refresh token to generate new access token.'''
        store = file.Storage('%s/%s'%(cred_path, token_file))
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('%s/%s'%(cred_path, credentials_file), self.scopes)
            creds = tools.run_flow(flow, store)
        return creds

    def get_events(self, start_datetime=None, end_datetime=None, calendar_name='primary', **kwargs):
        '''Return all events and metadata between start and end datetimes.'''

        if not start_datetime:
            start_datetime = datetime.datetime.utcnow()

        if not end_datetime:
            end_datetime = start_datetime + datetime.timedelta(days = 7)

        start_str = start_datetime.isoformat() + 'Z' # 'Z' indicates UTC time
        end_str = end_datetime.isoformat() + 'Z'
        events_result = self.calendar.events().list(calendarId=calendar_name,
                                                    timeMin=start_str,
                                                    timeMax=end_str,
                                                    singleEvents=True,
                                                    orderBy='startTime',
                                                    **kwargs).execute()
        return events_result.get('items', [])

    def get_scheduled_events(self, start_datetime=None, end_datetime=None, device_name=None, **kwargs):
        '''Given a device name and time range, get / parse / return all scheduled events.
           If no device name if given, default to all available calendars.'''
        all_events = []

        calendar_list = self.calendar.calendarList().list().execute()
        for c in calendar_list['items']:
            if not device_name or device_name == c['summary']:
                events = self.get_events(start_datetime=start_datetime,
                                         end_datetime=end_datetime,
                                         calendar_name=c['id'],
                                         **kwargs)
                all_events.extend([self.parse_event(event, c['summary'], c['id']) for event in events])

        return all_events # list of dicts for now

    def parse_event(self, event, calendar=None, calendar_id=None):
        '''Takes an input event resource from google calendar API and converts
           it to the desired output (a dict)'''
        # start time, end time, event name, event duration? ...
        return { 'event_id'   : event['id'],
                 'start_time' : event['start']['dateTime'] if 'dateTime' in event['start'].keys()
                                                           else event['start']['date'],
                 'end_time'   : event['end']['dateTime'] if 'dateTime' in event['end'].keys()
                                                         else event['end']['date'],
                 'action'     : event['summary'],
                 'created'    : event['created'],
                 'updated'    : event['updated'],
                 'calendar'   : calendar,
                 'calendar_id': calendar_id
               }
