# Weekly Zendesk Report Automation

This project automates the process of fetching a weekly report from a Zendesk Explore dashboard, analyzing it with Google Gemini AI, and updating a Google Slides presentation with the summary.

## Prerequisites

1.  **Python 3.8+**
2.  **Google Cloud Project** with the following APIs enabled:
    *   Google Slides API
    *   Google Generative AI API (Gemini)
3.  **Zendesk Account** with access to Explore dashboards.

## Setup

### 1. Install Dependencies

Navigate to the project directory and install the required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Configure Credentials

Create a `.env` file in this directory based on the following template:

```ini
# Google Cloud OAuth Credentials (downloaded JSON file path)
GOOGLE_CREDENTIALS_FILE=credentials.json
# Token file (automatically generated after first login)
GOOGLE_TOKEN_FILE=token.json

# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Zendesk Credentials
ZENDESK_EMAIL=your_email@domain.com
ZENDESK_PASSWORD=your_password
ZENDESK_DASHBOARD_URL=https://your_subdomain.zendesk.com/explore/dashboard_url
# Directory to download reports to
DOWNLOAD_DIR=downloads
```

#### Getting Google Credentials:
1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project.
3.  Enable **Google Slides API**.
4.  Go to **Credentials** -> **Create Credentials** -> **OAuth Client ID** (Application type: Desktop App).
5.  Download the JSON file and save it as `credentials.json` in this directory.
6.  Get a **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/) and add it to `.env`.

### 3. Customize Zendesk Logic

Zendesk Explore dashboards are complex and often use iframes. The provided `zendesk_bot.py` contains a generic structure but **requires you to inspect your specific dashboard** to find the correct CSS selectors for the "Export" button.

1.  Open `zendesk_bot.py`.
2.  Locate the `download_report` method.
3.  Update the `find_element` calls with the actual IDs, classes, or XPaths of your dashboard's export button.

## Usage

When you receive the weekly slide deck URL, run the script:

```bash
python main.py --slide_url "https://docs.google.com/presentation/d/YOUR_PRESENTATION_ID/edit"
```

### First Run
On the first run, a browser window will open asking you to log in to your Google account to authorize the Slides API.

## Testing

### Mock Mode
To test the automation flow without connecting to Zendesk or Gemini (useful for verifying Google Slides permissions and general logic), use the `--mock` flag:

```bash
python main.py --slide_url "https://docs.google.com/presentation/d/YOUR_PRESENTATION_ID/edit" --mock
```

This will:
1.  Generate a dummy CSV file locally (bypassing Zendesk).
2.  Generate a hardcoded analysis summary (bypassing Gemini).
3.  **Actually update** the Google Slides presentation (verifying the API connection works).

**Recommendation:** Create a blank "Sandbox" Google Slide deck and use its URL for testing to avoid messing up real reports.

## Automating the Trigger

Since the slide deck URL changes weekly and is shared via Google Chat:
1.  **Manual Trigger**: The simplest method is to copy the URL from the chat and run the command above.
2.  **Chat Bot (Advanced)**: To fully automate this, you would need to build a Google Chat App (Bot) that listens for messages containing slide URLs and triggers this script. This requires a published Google Workspace App and a webhook receiver, which is beyond the scope of this script but can be integrated by extending `main.py` to run as a web server (e.g., using Flask).

## Troubleshooting

*   **Zendesk Login Fails**: Check if your account requires SSO or 2FA. If so, you may need to use session cookies or a more complex Selenium login flow.
*   **Slides API Error**: Ensure the Google account you log in with has edit access to the presentation.
