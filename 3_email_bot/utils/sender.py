from __future__ import print_function
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv
from utils.reader import EmailReader
import os

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class EmailSender:
    def __init__(self):
        self.email = os.getenv("SEEDER_INCIDENTS_RECEIVER_EMAIL")   
        self.service = self.authenticate_gmail()

    def authenticate_gmail(self):
        """Authenticates with the Gmail API"""
        creds = None
        if os.path.exists('token_send.json'):
            creds = Credentials.from_authorized_user_file('token_send.json', SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('./credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            with open('token_send.json', 'w') as token:
                token.write(creds.to_json())

        service = build('gmail', 'v1', credentials=creds)
        return service

    def send_email(self, to_address, subject, body):
        """
        Sends a simple email using the Gmail API
        
        Args:
            to_address (str): Recipient's email address
            subject (str): Email subject
            body (str): Email body
            
        Returns:
            bool: True if the email was sent successfully, False otherwise
        """
        message = MIMEMultipart()
        message["To"] = to_address
        message["From"] = self.email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        try:
            response = self.service.users().messages().send(
                userId="me",
                body={"raw": raw_message}
            ).execute()
            
            # Check if the response contains a message ID (indicating success)
            if response and 'id' in response:
                print(f"Email sent successfully! ID: {response['id']}")
                return True
            else:
                print("Warning: Email sent, but without confirmation ID.")
                return True  # We still consider it a success if there's no error
        except Exception as e:
            print("Error sending email:", e)
            return False

    def reply_email(self, original_msg, reply_body, content_type="plain"):
        """
        Replies to an email using the Gmail API
        
        Args:
            original_msg (dict): Dictionary with information about the original email
            reply_body (str): Reply body
            content_type (str, optional): Content type (plain or html). Defaults to "plain".
            
        Returns:
            bool: True if the email was sent successfully, False otherwise
        """

        # Validation of essential fields
        required_fields = ["from_", "subject", "thread_id"]
        missing_fields = [field for field in required_fields if not original_msg.get(field)]

        if missing_fields:
            print(f"Error: Missing fields in the original email: {', '.join(missing_fields)}")
            return False

        msg = MIMEMultipart()
        msg["From"] = self.email
        msg["To"] = original_msg["from_"]
        msg["Subject"] = "Re: " + original_msg["subject"]

        message_id = original_msg.get("headers", {}).get("Message-ID")
        if message_id:
            msg["In-Reply-To"] = message_id
            msg["References"] = message_id

        msg.attach(MIMEText(reply_body, content_type))

        raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        try:
            response = self.service.users().messages().send(
                userId="me",
                body={"raw": raw_message, "threadId": original_msg["thread_id"]}
            ).execute()
            
            # Check if the response contains a message ID (indicating success)
            if response and 'id' in response:
                print(f"Reply sent successfully! ID: {response['id']}")
                return True
            else:
                print("Warning: Reply sent, but without confirmation ID.")
                return True  # We still consider it a success if there's no error
                
        except HttpError as error:
            print(f"Gmail API error: {error}")
            return False
        except Exception as e:
            print(f"Unexpected error sending reply: {e}")
            return False
