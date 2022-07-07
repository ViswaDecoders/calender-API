from setup import settings
from django.http import Http404
from django.shortcuts import render

import os
import datetime

from googleapiclient import discovery
from oauth2client import client,tools
from oauth2client.file import Storage
from googleapiclient.errors import HttpError
    
# Defining scopes of the API
SCOPES = 'https://www.googleapis.com/auth/calendar'
# Giving oAuth2 credentials to authenticate the API usage
CLIENT_SECRET_FILE = str(settings.BASE_DIR) + '/credentials/client_secrets.json'

def opening(request):
    return render(request,'home.html')

def GoogleCalendarInitView(request):
    # Login credentials with refresh token are get saved for future authentication
    credential_path = str(settings.BASE_DIR) + '/credentials/login_credentials.json'
    store = Storage(credential_path)
    credentials = store.get()
    # if no login credentials found, then re-auntheticate with avalable oAuth2 credentials
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flags = tools.argparser.parse_args(args=[])
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)
    return GoogleCalendarRedirectView(request, credentials)

def GoogleCalendarRedirectView(request, credentials):
    creds = credentials
    # Prints the starting time and name of the next 10 events on the user's calendar.
    try:
        service = discovery.build('calendar', 'v3', credentials=creds)

        now = datetime.datetime.utcnow().isoformat()+'Z'
        print('Getting the upcoming 10 events')
        # Calling the Calendar API
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        # Prints the starting time and name of the next 10 events
        for event in events:
            print("event: ",event)
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

    except HttpError as error:
        # any error encountered get prints
        raise Http404('An error occurred: %s' % error)
    return render(request, 'events.html', {'events': events,})