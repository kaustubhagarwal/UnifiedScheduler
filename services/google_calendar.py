import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import datetime
import pickle

class GoogleCalendarService:
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    def __init__(self):
        self.creds = None
        self.credentials_path = '.credentials'
        if not os.path.exists(self.credentials_path):
            os.makedirs(self.credentials_path)
        self.token_path = os.path.join(self.credentials_path, 'token.pickle')
        self.credentials_file = os.path.join(self.credentials_path, 'credentials.json')

    def authenticate(self):
        """Handles the OAuth2 flow for Google Calendar"""
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                self.creds = flow.run_local_server(port=0)

            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)

    def get_events(self, date):
        """Gets events from Google Calendar for a specific date"""
        try:
            if not self.creds:
                self.authenticate()

            service = build('calendar', 'v3', credentials=self.creds)

            # Get the start and end of the specified date
            start_time = datetime.datetime.combine(date, datetime.time.min).isoformat() + 'Z'
            end_time = datetime.datetime.combine(date, datetime.time.max).isoformat() + 'Z'

            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))

                # Convert to datetime objects
                start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))

                # Calculate duration
                duration = end_dt - start_dt
                duration_str = f"{int(duration.total_seconds() / 3600)} hours" if duration.total_seconds() >= 3600 else f"{int(duration.total_seconds() / 60)} minutes"

                formatted_events.append({
                    'title': event['summary'],
                    'start_time': start_dt.strftime('%H:%M'),
                    'duration': duration_str,
                    'source': 'Google Calendar'
                })

            return formatted_events

        except Exception as e:
            print(f"Error fetching Google Calendar events: {str(e)}")
            return []