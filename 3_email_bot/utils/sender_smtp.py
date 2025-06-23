from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from utils.reader import EmailReader
import os
import smtplib

load_dotenv()

# Backup Script to send emails via SMTP
class EmailSender:
    def __init__(self, smtp_server=None, smtp_port=None, email=None, password=None):
        self.smtp_server = smtp_server or "smtp.gmail.com"
        self.smtp_port = smtp_port or 587
        self.email = email or os.getenv("MAILER_ADDRESS")
        self.password = password or os.getenv("MAILER_PWD")

    def send_email(self, to_address, subject, body):
        # Create the message body
        msg = MIMEMultipart()
        msg["From"] = self.email
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Send the email via SMTP
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
        except Exception as e:
            print("Error sending email:", e)

    def reply_email(self, original_msg, reply_body):
        msg = MIMEMultipart()
        msg["From"] = self.email
        msg["To"] = original_msg.from_
        msg["Subject"] = "Re: " + original_msg.subject

        # Get the Message-ID from headers
        message_id = original_msg.headers.get("Message-ID", None)
        if message_id:
            msg["In-Reply-To"] = message_id
            msg["References"] = message_id

        msg.attach(MIMEText(reply_body, "plain"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
        except Exception as e:
            print("Error sending reply:", e)
