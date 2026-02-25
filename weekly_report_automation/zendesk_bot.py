import time
import os
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import config

class ZendeskBot:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        # Set download directory preference
        prefs = {
            "download.default_directory": config.DOWNLOAD_DIR,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        self.options.add_experimental_option("prefs", prefs)

        # Uncomment the next line to run in headless mode (no GUI)
        # self.options.add_argument("--headless")

        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        except Exception as e:
            print(f"Error initializing Chrome driver: {e}")
            raise

    def login(self):
        """Logs into Zendesk using credentials from config."""
        login_url = f"https://{config.ZENDESK_EMAIL.split('@')[1]}/auth/v2/login/signin" if config.ZENDESK_EMAIL and '@' in config.ZENDESK_EMAIL else "https://www.zendesk.com/login"
        # Note: The login URL above is a guess. Usually it's https://subdomain.zendesk.com/
        # User should probably set the full login URL or dashboard URL will redirect to login.

        print(f"Navigating to {config.ZENDESK_DASHBOARD_URL} (which should redirect to login if not authenticated)...")
        self.driver.get(config.ZENDESK_DASHBOARD_URL)

        # Check if we are on login page
        try:
            # Adjust these selectors based on the actual Zendesk login page structure
            # Common pattern: check for email input field
            try:
                email_field = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.NAME, "user[email]"))
                )
            except:
                print("Login page not detected or already logged in.")
                return

            password_field = self.driver.find_element(By.NAME, "user[password]")

            print("Entering credentials...")
            email_field.send_keys(config.ZENDESK_EMAIL)
            password_field.send_keys(config.ZENDESK_PASSWORD)

            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()

            # Wait for redirection back to dashboard or dashboard load
            print("Waiting for login to complete...")
            WebDriverWait(self.driver, 20).until(
                EC.url_contains("explore")
            )
            print("Login successful.")

        except Exception as e:
            print(f"Login process encountered an issue: {e}")

    def download_report(self):
        """
        Navigates to the dashboard and attempts to download the report.
        NOTE: This function contains placeholders for selectors that MUST be updated
        to match the specific Zendesk Explore dashboard structure.
        """
        print("Waiting for dashboard to load...")
        time.sleep(10) # Simple wait for full dashboard load (adjust as needed)

        try:
            # Zendesk Explore often uses iframes. You might need to switch to the content frame.
            # iframe = self.driver.find_element(By.CSS_SELECTOR, "iframe#target_iframe_id")
            # self.driver.switch_to.frame(iframe)

            # TODO: Inspect your dashboard and find the 'Export' button or the specific report's export option.
            # Example: finding a button by text or class
            # export_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Export')]")
            # export_button.click()

            # Example: Selecting CSV format
            # csv_option = self.driver.find_element(By.XPATH, "//li[contains(text(), 'CSV')]")
            # csv_option.click()

            print("CRITICAL: You need to implement the specific click logic for your dashboard export button in zendesk_bot.py")

            # Check if any file was downloaded (e.g. if user manually clicked during the wait)
            list_of_files = glob.glob(os.path.join(config.DOWNLOAD_DIR, "*"))
            if list_of_files:
                latest_file = max(list_of_files, key=os.path.getctime)
                # Check if file is recent (modified in last 2 mins)
                if time.time() - os.path.getctime(latest_file) < 120:
                     print(f"Detected downloaded file: {latest_file}")
                     return latest_file

            # Fail by default if no download logic is implemented
            raise NotImplementedError(
                "Automatic download logic not implemented. Please update zendesk_bot.py with correct selectors, "
                "or uncomment the mock data generation block for testing."
            )

            # --- MOCK DATA FOR TESTING (Uncomment below to test without Zendesk) ---
            # print("Simulating a download for demonstration (creating a dummy file)...")
            # mock_file = os.path.join(config.DOWNLOAD_DIR, "report.csv")
            # with open(mock_file, "w") as f:
            #     f.write("metric,value\nTickets Solved,120\nCSAT,98%\nResponse Time,2h")
            # return mock_file
            # -----------------------------------------------------------------------

        except Exception as e:
            print(f"Error downloading report: {e}")
            return None

    def close(self):
        self.driver.quit()
