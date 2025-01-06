import os
import pickle
# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type 

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

# Test the GmailHandler
if __name__ == "__main__":
    handler = GmailHandler()
    if handler.service:
        print("GmailHandler initialized successfully.")
    else:
        print("Failed to initialize GmailHandler.")

    
"""def gmail_command_executor(arguments, shortcuts, text_area,root_area,self):
      
      if not hasattr(gmail_command_executor, 'controller'):
        gmail_command_executor.controller=GmailHandler()"""
        
      
        