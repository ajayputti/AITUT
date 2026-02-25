import argparse
import os
import sys

# Add the current directory to sys.path to ensure modules are found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from zendesk_bot import ZendeskBot
from gemini_bot import GeminiBot
from slides_bot import SlidesBot

def main():
    parser = argparse.ArgumentParser(description="Automate Weekly Zendesk Report to Google Slides.")
    parser.add_argument("--slide_url", help="URL of the Google Slide deck to update", required=True)
    args = parser.parse_args()

    print("Starting Weekly Report Automation...")

    # 1. Download Data
    print("\n--- Step 1: Downloading Report from Zendesk ---")
    report_path = None
    try:
        zendesk = ZendeskBot()
        zendesk.login()
        report_path = zendesk.download_report()
        zendesk.close()

        if not report_path:
            print("Failed to download report. Exiting.")
            return
    except Exception as e:
        print(f"Zendesk error: {e}")
        # For testing purposes without credentials, we might want to continue if a mock file exists
        # But in production, we should stop.
        return

    # 2. Analyze Data
    print("\n--- Step 2: Analyzing Report with Gemini ---")
    analysis = ""
    try:
        gemini = GeminiBot()
        analysis = gemini.analyze_report(report_path)
        print("Analysis generated successfully.")
        print(f"Summary Preview: {analysis[:100]}...")
    except Exception as e:
        print(f"Gemini error: {e}")
        return

    # 3. Update Slides
    print("\n--- Step 3: Updating Google Slides ---")
    try:
        slides = SlidesBot()
        presentation_id = slides.get_presentation_id_from_url(args.slide_url)
        print(f"Target Presentation ID: {presentation_id}")
        slides.create_slide_with_text(presentation_id, "Weekly Zendesk Report Analysis", analysis)
        print("Slides updated successfully.")
    except Exception as e:
        print(f"Slides error: {e}")
        return

    print("\nAutomation Complete!")

if __name__ == "__main__":
    main()
