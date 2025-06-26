from __future__ import print_function
import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

# Scope for reading and modifying emails
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

# Gmail account data
class GoogleGmail:
    def __init__(self):
        self.service = self.authenticate_gmail()
        
    def authenticate_gmail(self):
        """Authenticates with OAuth2 and returns the Gmail API service"""
        # Dynamically find token and credentials paths
        token_path = os.path.join(os.path.dirname(__file__), 'gmail_token.json')
        credentials_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')

        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        service = build('gmail', 'v1', credentials=creds)
        return service

    def list_threads(self, service, max_results=1, query=None):
        """Lists recent threads (conversations), with filter option"""
        threads = service.users().threads().list(userId='me', maxResults=max_results, q=query).execute().get('threads', [])
        return threads

    def get_thread_messages(self, service, thread_id):
        """Returns all messages from a thread"""
        thread = service.users().threads().get(userId='me', id=thread_id, format='full').execute()
        return thread['messages']

    def extract_body(self, payload):
        """Recursively extracts the content of the message body"""
        if 'parts' in payload:
            for part in payload['parts']:
                # If the part is 'text/plain'
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    data = part['body']['data']
                    return base64.urlsafe_b64decode(data).decode().strip()
                # If the part is 'text/html'
                elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                    data = part['body']['data']
                    html = base64.urlsafe_b64decode(data).decode()
                    soup = BeautifulSoup(html, 'html.parser')
                    return soup.get_text().strip()
                # If the part has more parts inside it (multipart/alternative, etc)
                else:
                    result = self.extract_body(part)
                    if result:
                        return result
        else:
            # If there are no 'parts', try to get the body directly
            if 'body' in payload and 'data' in payload['body']:
                data = payload['body']['data']
                if data:
                    return base64.urlsafe_b64decode(data).decode().strip()

        return ''  # Return empty if nothing found

    def parse_message(self, message):
        """Wrapper to call the recursive parser"""
        return self.extract_body(message['payload'])

    def read_emails(self, max_results=10, query='is:unread'):
        """Reads emails and returns a simplified list with relevant fields"""
        threads = self.list_threads(self.service, max_results=max_results, query=query)

        emails = []
        for thread in threads:
            messages = self.get_thread_messages(self.service, thread['id'])

            for message in messages:
                headers = {h['name']: h['value'] for h in message['payload']['headers']}
                subject = headers.get('Subject', 'No subject')
                from_ = headers.get('From', 'Unknown')
                message_id = headers.get('Message-ID')  # Extracting the Message-ID
                text = self.parse_message(message)

                email = {
                    'from': from_,
                    'subject': subject,
                    'text': text,
                    'thread_id': message['threadId'],
                    'message_id': message_id,  # Message-ID from header
                    'id': message['id']  # Internal Gmail ID for operations like marking as read
                }
                emails.append(email)
        return emails

    def find_email_by_message_id(self, message_id):
        """Searches for a specific email by message_id in Gmail"""
        try:
            query = f"rfc822msgid:{message_id}"
            results = self.service.users().messages().list(userId="me", q=query).execute()
            messages = results.get('messages', [])

            if not messages:
                return None

            # Get the first result (should be unique)
            msg_id = messages[0]['id']
            msg = self.service.users().messages().get(userId="me", id=msg_id, format="full").execute()

            headers = {header['name']: header['value'] for header in msg['payload']['headers']}
            message_id = headers.get('Message-ID')

            return {
                "from": headers.get('From'),
                "subject": headers.get('Subject'),
                "message_id": message_id,
                "thread_id": msg.get('threadId'),
                "id": msg_id  # Adding the internal Gmail ID for use in other operations
            }
        except Exception as e:
            print(f"Error searching for email by message_id: {e}")
            return None
            
    def mark_as_read(self, message_id=None, thread_id=None):
        """
        Marks an email or thread as read in Gmail
        
        Args:
            message_id (str, optional): ID of the specific message to be marked as read
            thread_id (str, optional): ID of the thread to be marked as read
            
        Returns:
            bool: True if the operation was successful, False otherwise
            
        Note:
            At least one of the parameters (message_id or thread_id) must be provided
        """
        try:
            if not message_id and not thread_id:
                print("Error: You must provide message_id or thread_id")
                return False
                
            # If we have the message ID, we use it directly
            if message_id:
                result = self.service.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
                print(f"Email marked as read: {result.get('id')}")
                return True
                
            # If we only have the thread_id, we need to get all messages in the thread
            elif thread_id:
                # Get all messages in the thread
                thread = self.service.users().threads().get(userId='me', id=thread_id).execute()
                messages = thread.get('messages', [])
                
                # Mark each message as read
                for message in messages:
                    msg_id = message.get('id')
                    self.service.users().messages().modify(
                        userId='me',
                        id=msg_id,
                        body={'removeLabelIds': ['UNREAD']}
                    ).execute()
                
                print(f"Entire thread marked as read: {thread_id} ({len(messages)} messages)")
                return True
                
        except Exception as e:
            print(f"ERROR: Error marking email/thread as read: {e}")
            return False


def main():

    reader = GoogleGmail()

    print("Searching for recent unread threads...")
    threads = reader.list_threads(reader.service, max_results=10, query='is:unread')

    for thread in threads:
        print(f"\nThread ID: {thread['id']}")
        messages = reader.get_thread_messages(reader.service, thread['id'])

        for i, message in enumerate(messages):
            headers = {h['name']: h['value'] for h in message['payload']['headers']}
            subject = headers.get('Subject', 'No subject')
            from_ = headers.get('From', 'Unknown')
            text = reader.parse_message(message)

            print(f"\nEmail {i+1}")
            print(f"From: {from_}")
            print(f"Subject: {subject}")
            print(f"Body:\n{text[:50]}")

if __name__ == "__main__": 
    main()