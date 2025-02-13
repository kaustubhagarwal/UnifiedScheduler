import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import datetime
import pickle
from datetime import timezone
import pytz

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

            # Get the start and end of the specified date in local time
            local_tz = pytz.timezone('America/New_York')  # Replace with your local time zone
            local_start_time = datetime.datetime.combine(date, datetime.time.min).replace(tzinfo=local_tz)
            local_end_time = datetime.datetime.combine(date, datetime.time.max).replace(tzinfo=local_tz)

            # Convert to UTC for Google Calendar API
            start_time = local_start_time.astimezone(pytz.utc).isoformat()
            end_time = local_end_time.astimezone(pytz.utc).isoformat()

            # Fetch events within this range
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
                # Handle all-day vs timed events
                if 'dateTime' in event['start']:
                    start = event['start']['dateTime']
                    end = event['end']['dateTime']
                else:  # All-day event
                    start = event['start']['date']
                    end = event['end']['date']

                # Convert to datetime objects (handle both date and dateTime)
                if 'T' in start:  # Timed event
                    start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00')).astimezone(local_tz)
                    end_dt = datetime.datetime.fromisoformat(end.replace('Z', '+00:00')).astimezone(local_tz)
                else:  # All-day event
                    start_dt = datetime.datetime.strptime(start, '%Y-%m-%d').replace(tzinfo=local_tz)
                    end_dt = datetime.datetime.strptime(end, '%Y-%m-%d').replace(tzinfo=local_tz)

                # Calculate duration
                duration = end_dt - start_dt
                duration_str = f"{int(duration.total_seconds() / 3600)} hours" if duration.total_seconds() >= 3600 else f"{int(duration.total_seconds() / 60)} minutes"

                formatted_events.append({
                    'title': event.get('summary', 'No Title'),
                    'start_time': start_dt.strftime('%H:%M'),
                    'duration': duration_str,
                    'source': 'Google Calendar'
                })

            return formatted_events

        except Exception as e:
            print(f"Error fetching Google Calendar events: {str(e)}")
            return []