import datetime
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Read-only calendar access scope
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class GoogleCalendar: 
    def __init__(self):
        self.creds = None
        # Token stored locally after login
        token_path = os.path.join(os.path.dirname(__file__), 'calendar_token.json')
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        # Login and authorization via browser (on first execution)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                credentials_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Save token for reuse
            with open(token_path, 'w') as token:
                token.write(self.creds.to_json())

        # API connection
        self.service = build('calendar', 'v3', credentials=self.creds)

    def consult(self):
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                                   maxResults=10, singleEvents=True,
                                                   orderBy='startTime').execute()
        events = events_result.get('items', [])
        response = []
        
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            response.append({
                'summary': event['summary'],
                'start': start
            })

        return response    

if __name__ == '__main__':
    calendar = GoogleCalendar()
    events = calendar.consult()
    print("Upcoming events:", events)
