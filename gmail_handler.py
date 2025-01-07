import os
import pickle
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type


from new_interfaces import send_email_interface

class GmailHandler:
    def __init__(self):
        self.scopes = ['https://mail.google.com/']
        self.email = 'pratik.surin22b@iiitg.ac.in'
        self.service = self.gmail_authenticate()
    
    def gmail_authenticate(self):
        """Authenticate and return the Gmail service object."""
        creds = None
        try:
            # Check if token.pickle exists for stored credentials
            if os.path.exists("token.pickle"):
                with open("token.pickle", "rb") as token:
                    creds = pickle.load(token)
            
            # If no credentials or they are invalid, refresh or prompt for login
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.scopes)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for next time
                with open("token.pickle", "wb") as token:
                    pickle.dump(creds, token)
            
            # Build the Gmail service
            return build('gmail', 'v1', credentials=creds)
        
        except Exception as e:
            print(f"Failed to authenticate Gmail connection: {e}")
            return None

    def add_attachment(self, message, file_path):
        """Add an attachment to a MIME message."""
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        content_type, encoding = guess_type(file_path)
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        
        main_type, sub_type = content_type.split('/', 1)
        
        with open(file_path, 'rb') as fp:
            if main_type == 'text':
                msg = MIMEText(fp.read().decode(), _subtype=sub_type)
            elif main_type == 'image':
                msg = MIMEImage(fp.read(), _subtype=sub_type)
            elif main_type == 'audio':
                msg = MIMEAudio(fp.read(), _subtype=sub_type)
            else:
                msg = MIMEBase(main_type, sub_type)
                msg.set_payload(fp.read())
                encoders.encode_base64(msg)
        
        filename = os.path.basename(file_path)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

    def build_message(self, destination, obj, body, attachments=None):
        """Build an email message."""
        if attachments is None:
            attachments = []
        
        if not attachments:  # No attachments
            message = MIMEText(body)
            message['to'] = destination
            message['from'] = self.email
            message['subject'] = obj
        else:  # With attachments
            message = MIMEMultipart()
            message['to'] = destination
            message['from'] = self.email
            message['subject'] = obj
            message.attach(MIMEText(body))
            
            for filename in attachments:
                self.add_attachment(message, filename)  # Correctly use the instance method
        
        return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}
    
    def send_message(self, destination, obj, body, attachments=None):
        """Send an email message."""
        if attachments is None:
            attachments = []
        
        raw_message = self.build_message(destination, obj, body, attachments)
        return self.service.users().messages().send(
            userId="me",
            body=raw_message
        ).execute()


def gmail_command_executor(arguments, shortcuts, text_area,root_area,self):
    
      controller=GmailHandler()
      
      if(arguments[0]=="send"):
          send_email_interface()
        
      
        