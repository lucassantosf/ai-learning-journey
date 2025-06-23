from imap_tools import MailBox, AND
from dotenv import load_dotenv
import os

load_dotenv()

# Backup Script to read emails using IMAP
class EmailReader:
    def __init__(self, params):
        self.params = params
        self.email = os.getenv("MAILER_ADDRESS")
        self.password = os.getenv("MAILER_PWD")
        self.seen = params.get("seen", False)

    def read_emails(self):
        emails = []
        with MailBox("imap.gmail.com").login(self.email, self.password, initial_folder="INBOX") as mailbox:
            for msg in mailbox.fetch(AND(seen=self.seen), limit=10, reverse=True):
                is_reply = "In-Reply-To" in msg.headers  # checks if the header exists
                emails.append({
                    "id": msg.uid,
                    "from": msg.from_,
                    "subject": msg.subject,
                    "text": msg.text,
                    "is_reply": is_reply,
                    "in_reply_to": msg.headers.get("In-Reply-To", None),
                    "message_id": msg.headers.get("Message-ID", None),
                    "raw": msg,
                })
        return emails
