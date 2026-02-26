import pandas as pd
from google import genai
import config

class GeminiBot:
    def __init__(self, mock=False):
        self.mock = mock
        if self.mock:
            self.client = None
            print("Running in MOCK mode: Gemini API will not be called.")
        elif not config.GEMINI_API_KEY:
            print("Warning: GEMINI_API_KEY is not set. Using a mock response.")
            self.client = None
        else:
            self.client = genai.Client(api_key=config.GEMINI_API_KEY)

    def analyze_report(self, file_path):
        """Reads the report file and uses Gemini to generate a summary."""
        try:
            # Read file based on extension
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                return f"Error: Unsupported file format for {file_path}"

            # Convert dataframe to string representation
            data_str = df.to_string()

            if self.mock:
                return f"Simulated Gemini Response (MOCK MODE) for data:\n{data_str}\n\n* Key Highlights:\n  - Metric A is good.\n* Areas of Concern:\n  - None."

            # Prepare Prompt
            prompt = f"""
            You are a helpful data analyst. Here is the weekly Zendesk report data:

            {data_str}

            Please provide a summary of the key metrics for a weekly business review slide.
            Include:
            1. Key Highlights (bullet points)
            2. Areas of Concern
            3. Recommendations

            Keep the text concise and professional.
            """

            if self.client:
                # Using 'gemini-1.5-flash' model
                response = self.client.models.generate_content(
                    model='gemini-1.5-flash', contents=prompt
                )
                return response.text
            else:
                return f"Simulated Gemini Response (MISSING KEY) for data:\n{data_str}\n\n[Summary would be here if API key was provided]"

        except Exception as e:
            return f"Error analyzing report: {str(e)}"
