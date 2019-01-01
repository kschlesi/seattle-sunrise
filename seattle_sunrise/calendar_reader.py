'''
A class for reading scheduled events from a google calendar
Requires proper auth tokens for oauth2 in an external directory
'''
__all__ = []

import datetime
import requests
import pytz
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

def error_logger(func, *args, **kwargs):
    '''executes a function; catches errors and logs them'''
    def new_func(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
        except Exception as e:
            # log error (add message?)
            print('ERROR ({}): {} caught in calendar_reader.{}'.format(datetime.datetime.utcnow(),
                                                                       e.__class__.__name__,
                                                                       func.__name__
                                                                       ))
            return None
        else:
            return response
    return new_func

__all__.append('CalendarReader')
class CalendarReader():

    def __init__(self,
                 credentials_path,
                 token_file='token.json',
                 credentials_file='credentials.json'):
        self.scopes = 'https://www.googleapis.com/auth/calendar.readonly'
        creds = self.get_credentials_with_browser_flow(credentials_path, token_file, credentials_file)
        self.calendar = build('calendar', 'v3', http=creds.authorize(Http()))

    def get_credentials_with_browser_flow(self, credentials_path, token_file, credentials_file):
        '''Run authorization procedure. Use valid access token if it exists;
           otherwise, use refresh token to generate new access token.'''
        store = file.Storage('%s/%s'%(credentials_path, token_file))
        creds = store.get()
        print('creds exist' if creds else 'no creds exist')
        print('tokens invalid' if creds.invalid else 'tokens valid')
        if not creds or creds.invalid:
            print('generating new tokens...')
            flow = client.flow_from_clientsecrets('%s/%s'%(credentials_path, credentials_file), self.scopes)
            creds = tools.run_flow(flow, store)
        return creds

    @error_logger
    def get_events(self, start_datetime=None, end_datetime=None, calendar_name='primary', **kwargs):
        '''Return all events and metadata between start and end datetimes.'''

        if not start_datetime:
            start_datetime = datetime.datetime.utcnow()

        if not end_datetime:
            end_datetime = start_datetime + datetime.timedelta(days = 7)

        events_result = self.calendar.events().list(calendarId=calendar_name,
                                                    timeMin=start_datetime.isoformat() + 'Z', # 'Z' indicates UTC time
                                                    timeMax=end_datetime.isoformat() + 'Z',
                                                    singleEvents=True,
                                                    orderBy='startTime',
                                                    **kwargs).execute()
        return events_result.get('items', [])

    @error_logger
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
                if events is None:
                    raise TypeError('get_events failed to return events')
                all_events.extend([self.parse_event(event, c['summary'], c['id']) for event in events
                                                                                  if is_valid(event)])
        return all_events # list of dicts

    def parse_event(self, event, calendar=None, calendar_id=None):
        '''Takes an input event resource from google calendar API and converts
           it to the desired output (a dict)'''
        return { 'event_id'   : event['id'],
                 'start_time' : parse_gtime(event['start']['dateTime']) if 'dateTime' in event['start'].keys()
                                                                        else parse_gtime(event['start']['date'], 'date'),
                 'end_time'   : parse_gtime(event['end']['dateTime'])   if 'dateTime' in event['end'].keys()
                                                                        else parse_gtime(event['end']['date'], 'date'),
                 'action'     : event.get('summary'),
                 'created'    : parse_gtime(event['created']),
                 'updated'    : parse_gtime(event['updated']),
                 'calendar'   : calendar,
                 'calendar_id': calendar_id
               }


def is_valid(event):
    '''determines whether event is valid (for now, this means it has start and end datetimes)'''
    return 'dateTime' in event['start'].keys() and 'dateTime' in event['end'].keys()

def parse_gtime(dt_str, type='datetime'):
    '''parses stupid google style datetime string'''
    if type=='date':
        return datetime.datetime.strptime(dt_str, '%Y-%m-%d')
    # else, treat as datetime
    if dt_str[-1] == 'Z': # UTC time
        return datetime.datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    else: # has UTC offset
        c = dt_str.rfind(':') # have to remove final : in string :(
        return datetime.datetime.strptime(dt_str[:c] + dt_str[c+1:], '%Y-%m-%dT%H:%M:%S%z').astimezone(pytz.utc).replace(tzinfo=None)
