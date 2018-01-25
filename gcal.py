from __future__ import print_function
import httplib2
import os
from util import *
import pdb
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import enum
import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'google_client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


class GColorId(enum.Enum):
    GREEN = 2,
    RED = 11


class GCalendar(object):
    def __init__(self, calendar_id):
        self.calendar_id = calendar_id
        self.event_id = None
        self.start_tm = None
        self.description = None
        self.credentials = self.get_credentials()
        self.http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('calendar', 'v3', http=self.http)

    def get_backup_paths(self):
        event = self.service.events().get(
            calendarId=self.calendar_id, eventId=self.event_id).execute()
        if event:
            self.description = (event['description']).encode('ascii', 'ignore')
            return self.description.split('\n')
        return None

    @staticmethod
    def generate_report(results=None):
        description = str_join("Backup Report\n",
                               "--------------------------")
        for result in results:
            path = result.get("path", "")
            errors = result.get("Errors", "-1")
            transferred = result.get("Transferred", "-1")
            log = result.get("log")
            description = str_join(
                description,
                "\nPath        : ", path,
                "\nErrors      : ", errors,
                "\nLog file    : ", log,
                "\nTransferred : ", transferred,
                "\n")
        return description

    def update_gevent(self, results=None, error=-1):
        # Color the event with GREEN for success
        color_id = GColorId.RED
        if error == 0:
            color_id = GColorId.GREEN

        if results:
            description = self.generate_report(results)

        body = {
            "colorId": "{}".format(color_id.value[0]),
            "description": str_join(self.description, "\n\n", description)
        }
        self.service.events().patch(calendarId=self.calendar_id,
                                    eventId=self.event_id,
                                    body=body).execute()

    @staticmethod
    def get_credentials():
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'calendar-python-quickstart.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:
                # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
                print('Storing credentials to ' + credential_path)
        return credentials

    def get_next_gevent(self, calendar_id=None):
        """Shows basic usage of the Google Calendar API.

        Creates a Google Calendar API service object and outputs a list of the next
        10 events on the user's calendar.
        """

        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        print('Getting the upcoming events')
        eventsResult = self.service.events().list(
            calendarId=self.calendar_id, timeMin=now, maxResults=1, singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])

        if not events:
            return dict()

        start_tm = events[0]['start'].get('dateTime', events[0]['start'].get('date'))
        self.event_id = events[0]['id']
        self.start_tm = start_tm
        return dict({"eventId": events[0]['id'],
                     "start_tm": start_tm,
                     "action": events[0]['summary']})


if __name__ ==  "__main__":
    gc = GCalendar("gdmhdc1p72eqsgme87cb77m8d8@group.calendar.google.com")
    event_id = gc.get_next_gevent()
    print (event_id)