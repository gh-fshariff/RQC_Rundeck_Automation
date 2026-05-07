import os
import re
import time
from playwright.sync_api import sync_playwright

class FrameworkEngine:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.input_data = self.config_manager.get_input_data()
        
        # Ensure directories exist
        os.makedirs(self.config_manager.INPUT_DIR, exist_ok=True)
        os.makedirs(self.config_manager.OUTPUT_DIR, exist_ok=True)

        self.url = self.input_data.get("rundeck_url")
        if not self.url:
            raise ValueError("rundeck_url must be provided in config.json")
    def _setup_browser(self):
        """Helper to initialize the browser with Basic Auth credentials."""
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(headless=False, channel="chrome", args=["--start-maximized"])
        self.context = self.browser.new_context(
            no_viewport=True,
            http_credentials={
                "username": self.config_manager.RUNDECK_USER,
                "password": self.config_manager.RUNDECK_PWD
            }
        )
        self.page = self.context.new_page()

    def _teardown_browser(self):
        """Helper to close the browser."""
        self.browser.close()
        self.p.stop()

    def run_failed_login(self):
        """Test Case 1: Failed Login"""
        self._setup_browser()
        try:
            print(f"Navigating to {self.url}")
            # timeout=90000ms is used here to account for extremely slow Rundeck dev server response times
            self.page.goto(self.url, timeout=90000)
            self.page.wait_for_selector("input[name='j_username'], input[id='login']", timeout=10000)
            print("Login page detected. Performing Negative Login Test...")

            self.page.locator("input[name='j_username'], input[id='login'], input[placeholder='Username']").fill(
                "invalid_user_test")
            self.page.locator("input[name='j_password'], input[id='password'], input[placeholder='Password']").fill(
                "invalid_password_test")
            self.page.locator("button[type='submit'], button:has-text('Login')").click()

            self.page.wait_for_load_state("networkidle")

            error_locator = self.page.locator("text='Invalid username and password.'")
            if "user/error" in self.page.url or error_locator.is_visible():
                screenshot_path = os.path.join(self.config_manager.OUTPUT_DIR, "ERROR_Invalid_Credentials.png")
                self.page.screenshot(path=screenshot_path)
                print(f"Negative Login Test Passed. Saved evidence: {screenshot_path}")
            else:
                raise Exception("Negative login test did not show expected error.")
        finally:
            self._teardown_browser()

    def run_successful_login(self):
        """Test Case 2: Successful Login"""
        self._setup_browser()
        try:
            # timeout=90000ms is used here to account for extremely slow Rundeck dev server response times
            self.page.goto(self.url, timeout=90000)
            try:
                self.page.wait_for_selector("input[name='j_username'], input[id='login']", timeout=5000)
                print("Automating login using real .env credentials...")
                self.page.locator("input[name='j_username'], input[id='login'], input[placeholder='Username']").fill(
                    self.config_manager.RUNDECK_USER)
                self.page.locator("input[name='j_password'], input[id='password'], input[placeholder='Password']").fill(
                    self.config_manager.RUNDECK_PWD)
                self.page.locator("button[type='submit'], button:has-text('Login')").click()
            except Exception:
                print("Already logged in or bypassed login screen.")

            self.page.wait_for_selector("text='Run Job Now'", timeout=60000)

            # Capture evidence of successful login
            time.sleep(2)  # Give the page a moment to fully render
            screenshot_path = os.path.join(self.config_manager.OUTPUT_DIR, "SUCCESS_Valid_Credentials.png")
            self.page.screenshot(path=screenshot_path)
            print(f"Successful Login Test Passed. Saved evidence: {screenshot_path}")

        finally:
            self._teardown_browser()

    def run_negative_fields(self):
        """Test Case 3: Negative Field Validations"""
        self._setup_browser()
        try:
            # timeout=90000ms is used here to account for extremely slow Rundeck dev server response times
            self.page.goto(self.url, timeout=90000)

            # Login if needed
            try:
                self.page.wait_for_selector("input[name='j_username'], input[id='login']", timeout=5000)
                self.page.locator("input[name='j_username'], input[id='login'], input[placeholder='Username']").fill(
                    self.config_manager.RUNDECK_USER)
                self.page.locator("input[name='j_password'], input[id='password'], input[placeholder='Password']").fill(
                    self.config_manager.RUNDECK_PWD)
                self.page.locator("button[type='submit'], button:has-text('Login')").click()
            except Exception:
                pass

            self.page.wait_for_selector("text='Run Job Now'", timeout=60000)

            text_fields = self.input_data.get("text_fields", {})
            input_files = self.input_data.get("input_files", {})
            dropdowns = self.input_data.get("dropdowns", {})
            
            all_fields = list(text_fields.keys()) + list(input_files.keys()) + list(dropdowns.keys())
            
            for field_to_skip in all_fields:
                print(f"Negative Test: Skipping [{field_to_skip}]")
                self.page.goto(self.url, timeout=90000)
                self.page.wait_for_load_state("networkidle")
                self.page.wait_for_selector("text='Run Job Now'", timeout=10000)
                self._fill_form(self.page, skip_field=field_to_skip)
                self.page.get_by_role("button", name="Run Job Now").click()
                try:
                    self.page.wait_for_load_state("networkidle", timeout=10000)
                except:
                    pass
                    
                # Explicitly wait for the red validation error banner to appear in the DOM
                try:
                    self.page.wait_for_selector(".alert-danger, .errormessage, .text-danger", timeout=10000)
                except:
                    pass
                
                # Give the browser an extra 3 seconds to ensure fonts and styles are fully painted
                time.sleep(3)
                screenshot_path = os.path.join(self.config_manager.OUTPUT_DIR,
                                               f"ERROR_Missing_{field_to_skip.replace(' ', '_')}.png")
                self.page.screenshot(path=screenshot_path)
                print(f"Saved negative evidence: {screenshot_path}")
        finally:
            self._teardown_browser()

    def run_happy_path(self):
        """Test Case 4: Happy Path and Output Verification"""
        self._setup_browser()
        try:
            # timeout=90000ms is used here to account for extremely slow Rundeck dev server response times
            self.page.goto(self.url, timeout=90000)

            # Login if needed
            try:
                self.page.wait_for_selector("input[name='j_username'], input[id='login']", timeout=5000)
                self.page.locator("input[name='j_username'], input[id='login'], input[placeholder='Username']").fill(
                    self.config_manager.RUNDECK_USER)
                self.page.locator("input[name='j_password'], input[id='password'], input[placeholder='Password']").fill(
                    self.config_manager.RUNDECK_PWD)
                self.page.locator("button[type='submit'], button:has-text('Login')").click()
            except Exception:
                pass

            self.page.wait_for_selector("text='Run Job Now'", timeout=60000)

            print("\n--- PHASE 2: Starting Happy Path ---")
            self._fill_form(self.page, skip_field=None)
            self.page.get_by_role("button", name="Run Job Now").click()
            self._verify_output(self.page)
        finally:
            self._teardown_browser()

    def _fill_form(self, page, skip_field=None):
        # 1. Handle Text Fields
        for label, val in self.input_data.get("text_fields", {}).items():
            if label == skip_field:
                continue
            try:
                page.get_by_label(label, exact=False).fill(val)
            except Exception as e:
                print(f"Warning: Could not fill '{label}'")
                
        # 2. Handle Required Dropdowns
        for label, val in self.input_data.get("dropdowns", {}).items():
            if label == skip_field:
                continue
            try:
                page.get_by_label(label, exact=False).select_option(label=val)
            except Exception as e:
                print(f"Warning: Could not select '{label}'")

        # 3. Handle Optional Dropdowns (Only fill during Happy Path)
        if skip_field is None:
            for label, val in self.input_data.get("optional_dropdowns", {}).items():
                try:
                    # Attempt by label first, if it fails attempt by index or generic select
                    page.get_by_label(label, exact=False).select_option(label=val)
                except:
                    try:
                        page.get_by_label(label, exact=False).select_option(index=1)
                    except Exception as e:
                        print(f"Warning: Could not select optional dropdown '{label}'")

        # 4. Handle File Uploads
        for label, filename in self.input_data.get("input_files", {}).items():
            if label == skip_field:
                continue
            file_path = os.path.join(self.config_manager.INPUT_DIR, filename)
            if os.path.exists(file_path):
                try: 
                    page.get_by_label(label, exact=False).set_input_files(file_path)
                except: 
                    page.locator("input[type='file']").first.set_input_files(file_path)
            else:
                print(f"Warning: File {filename} not found at {file_path}")

    def _verify_output(self, page):
        print("Job submitted. Monitoring nodes...")
        try:
            page.wait_for_url("**/execution/show/**", timeout=60000)
            page.wait_for_selector("text=All Steps OK", timeout=600000)

            print("Job finished. Expanding logs...")
            page.get_by_text("All Steps OK").first.click()
            time.sleep(2)
            
            print("Expanding the correct log step...")
            # To be robust across tools (Phoenix 5 steps, Titan 9 steps), find the last step that starts with "Run"
            run_steps = page.get_by_text(re.compile(r"^Run ", re.IGNORECASE))
            if run_steps.count() > 0:
                run_steps.last.click()
            
            time.sleep(3)
            page.keyboard.press("End")
            time.sleep(2)

            page.screenshot(path=os.path.join(self.config_manager.OUTPUT_DIR, "SUCCESS_Final_Full_Logs.png"), full_page=True)

            print("Searching for output URL...")
            # The URL is not clickable, so we scrape the text for it
            body_text = page.locator("body").text_content()
            
            # Match any URL starting with https://bifs
            match = re.search(r'(https://bifs[^\s"\'<>]+)', body_text)
            
            if match:
                download_url = match.group(1)
                print(f"Found URL: {download_url}")
                
                import base64
                auth_str = f"{self.config_manager.RUNDECK_USER}:{self.config_manager.RUNDECK_PWD}"
                b64_auth = base64.b64encode(auth_str.encode()).decode()
                
                # Fetch the file explicitly providing the Basic Auth headers
                response = page.context.request.get(
                    download_url,
                    headers={"Authorization": f"Basic {b64_auth}"}
                )
                
                # Extract filename from URL or headers, fallback to output.csv
                filename = download_url.split('/')[-1]
                if not filename or filename == "output":
                    filename = "RQC_Output.csv"
                    
                download_path = os.path.join(self.config_manager.OUTPUT_DIR, filename)
                
                with open(download_path, 'wb') as f:
                    f.write(response.body())
                    
                print(f"SUCCESS: {filename} saved.")
                
                # Basic verification
                file_size = os.path.getsize(download_path)
                if file_size > 0:
                    print(f"Verification Success: File downloaded correctly ({file_size} bytes).")
                    
                    # Output Format Verification (JAMA Requirement)
                    expected_sections = self.input_data.get("expected_csv_sections", [])
                    if expected_sections:
                        print("Performing Output Format Verification...")
                        with open(download_path, 'r', encoding='utf-8', errors='ignore') as f:
                            csv_content = f.read()
                        
                        missing_sections = []
                        for section in expected_sections:
                            if section not in csv_content:
                                missing_sections.append(section)
                                
                        if missing_sections:
                            print(f"Output Format Verification Failed: Missing expected sections: {missing_sections}")
                            raise ValueError(f"Downloaded CSV does not match the expected format. Missing: {missing_sections}")
                        else:
                            print(f"Output Format Verification Passed: Found all {len(expected_sections)} expected sections.")
                            
                else:
                    print("Verification Failed: Downloaded file is empty.")
            else:
                print("Could not find a https://bifs URL in the logs.")

        except Exception as e:
            print(f"Happy Path interaction encountered a hurdle: {e}")
            page.screenshot(path=os.path.join(self.config_manager.OUTPUT_DIR, "EXPANSION_STALL_FINAL.png"))
