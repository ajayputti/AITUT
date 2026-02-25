import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Google Cloud Credentials
# Path to the OAuth 2.0 Client Secret JSON file downloaded from Google Cloud Console
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
# Path to store the user's access and refresh tokens
GOOGLE_TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")

# Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Zendesk Credentials
ZENDESK_EMAIL = os.getenv("ZENDESK_EMAIL")
ZENDESK_PASSWORD = os.getenv("ZENDESK_PASSWORD")
ZENDESK_DASHBOARD_URL = os.getenv("ZENDESK_DASHBOARD_URL")

# Directory to store downloaded reports
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", os.path.join(os.getcwd(), "downloads"))

# Ensure download directory exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
