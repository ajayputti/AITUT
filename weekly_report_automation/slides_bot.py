import os.path
import re
import uuid
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import config

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/presentations']

class SlidesBot:
    def __init__(self):
        """Authenticates with Google Slides API."""
        self.creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists(config.GOOGLE_TOKEN_FILE):
            try:
                self.creds = Credentials.from_authorized_user_file(config.GOOGLE_TOKEN_FILE, SCOPES)
            except Exception as e:
                print(f"Error loading credentials: {e}")
                self.creds = None

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception:
                    print("Token expired and refresh failed. Please re-authenticate.")
                    self.creds = None

            if not self.creds:
                if not os.path.exists(config.GOOGLE_CREDENTIALS_FILE):
                     # If we are in a headless environment without credentials, we can't proceed with auth flow easily.
                     # We'll just print a warning and let the script fail if it tries to use the API.
                     print(f"Credentials file '{config.GOOGLE_CREDENTIALS_FILE}' not found. Google Slides API will not work.")
                     return

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        config.GOOGLE_CREDENTIALS_FILE, SCOPES)
                    # This requires a browser. If running on a server, one needs to auth locally and copy token.json
                    print("Initiating authentication flow. This requires a browser.")
                    self.creds = flow.run_local_server(port=0)

                    # Save the credentials for the next run
                    with open(config.GOOGLE_TOKEN_FILE, 'w') as token:
                        token.write(self.creds.to_json())
                except Exception as e:
                    print(f"Authentication failed: {e}")
                    return

        self.service = build('slides', 'v1', credentials=self.creds)

    def get_presentation_id_from_url(self, url):
        """Extracts the presentation ID from a Google Slides URL."""
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        if match:
            return match.group(1)
        # Try to handle if just ID is passed
        if re.match(r'^[a-zA-Z0-9-_]+$', url):
            return url
        raise ValueError("Invalid Google Slides URL")

    def create_slide_with_text(self, presentation_id, title_text, body_text):
        """Creates a new slide and adds the provided text."""
        if not hasattr(self, 'service'):
            print("Google Slides service not initialized.")
            return

        try:
            # 1. Create a new slide
            # Let API generate the objectId to avoid collisions
            requests = [
                {
                    'createSlide': {
                        'insertionIndex': '1', # Insert as the second slide (after title)
                        'slideLayoutReference': {
                            'predefinedLayout': 'TITLE_AND_BODY'
                        }
                    }
                }
            ]

            body = {'requests': requests}
            response = self.service.presentations().batchUpdate(
                presentationId=presentation_id, body=body).execute()

            create_slide_response = response.get('replies')[0].get('createSlide')
            slide_id = create_slide_response.get('objectId')
            print(f"Created new slide with ID: {slide_id}")

            # 2. Get the slide to find placeholders
            # We only fetch the specific slide's page elements to find placeholders
            presentation = self.service.presentations().get(
                presentationId=presentation_id).execute()

            # Find the slide we just created
            slide = next((s for s in presentation.get('slides') if s.get('objectId') == slide_id), None)

            if not slide:
                print("Error: Could not find the created slide.")
                return

            title_id = None
            body_id = None

            # Identify placeholders
            if 'pageElements' in slide:
                for element in slide['pageElements']:
                    if 'shape' in element and 'placeholder' in element['shape']:
                        type_ = element['shape']['placeholder']['type']
                        if type_ == 'TITLE' or type_ == 'CENTERED_TITLE':
                            title_id = element['objectId']
                        elif type_ == 'BODY':
                            body_id = element['objectId']

            # 3. Insert text into placeholders
            requests = []
            if title_id:
                requests.append({
                    'insertText': {
                        'objectId': title_id,
                        'text': title_text
                    }
                })

            if body_id:
                requests.append({
                    'insertText': {
                        'objectId': body_id,
                        'text': body_text
                    }
                })

            # Also format the body text to be bullet points if it's not already?
            # For now, just raw text insertion.

            if requests:
                body = {'requests': requests}
                self.service.presentations().batchUpdate(
                    presentationId=presentation_id, body=body).execute()
                print(f"Slide content updated successfully in presentation {presentation_id}.")
            else:
                print("Could not find placeholders on the new slide.")

        except Exception as e:
            print(f"Error updating slides: {e}")
            raise
