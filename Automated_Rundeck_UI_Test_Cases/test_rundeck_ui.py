import os
import sys
from pathlib import Path

# Add the root directory to sys.path so we can import from libraries
TOP_OF_TOOL_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(TOP_OF_TOOL_PATH))

from libraries.config import Config
from libraries.framework_engine import FrameworkEngine

def test_rundeck_ui_automation():
    """
    Description:
        This test case's purpose is to test the happy path and negative path of the Rundeck Run Quality Control (RQC) tool. \
        This test case verifies that required fields correctly throw errors when skipped, and that the happy path \
        successfully triggers a run, completes with 'All Steps OK', and produces a valid output CSV file.

    Prerequisites:
        - Predetermined output location is available
        - Valid required inputs and configurations are present for the tool inside data/config.json
        - .env file containing RUNDECK_USER and RUNDECK_PWD is present

    Test Data:
        1) A valid input sheet (e.g. SampleSheet) and any other required CSVs in the data/ folder
        2) Text fields configured in data/config.json
        3) Dropdown options configured in data/config.json

    Steps:
        1) Navigate to the Rundeck Job URL.
        2) Perform Negative Login Test:
            - Enter invalid username and password and submit.
            - Verify the 'Invalid username and password' error appears and capture a screenshot.
            - Enter real .env credentials to successfully login.
            ER: A screenshot of the invalid credentials error is captured and successful login follows.
        3) Perform Negative Field Testing:
            - Iterate through every required text field, dropdown, and file upload defined in config.json.
            - For each field, skip filling it while filling all others.
            - Click 'Run Job Now' and take a screenshot of the error.
            ER: A screenshot is captured for each missing field demonstrating validation prevents execution.
        4) Perform Happy Path Testing:
            - Fill all required text fields, dropdowns, and file uploads.
            - Fill any optional dropdowns (e.g. BIP root directory).
            - Click 'Run Job Now'.
            ER: The job starts successfully and the execution log page is loaded.
        4) Monitor Execution:
            - Wait for 'All Steps OK' status.
            - Expand the final execution step.
            - Capture a screenshot of the completed log.
            ER: The final log is expanded and a screenshot is saved.
        5) Validate Output:
            - Scrape the final execution log for a download URL.
            - Fetch the file directly using the authenticated session.
            - Verify the file is downloaded and its size is greater than 0 bytes.
            ER: The output file is saved to the outputs/ directory and validated.
        6) Verify Output Format:
            - Read the downloaded output CSV.
            - Cross-reference the file contents against the 'expected_csv_sections' array defined in config.json.
            ER: The output CSV contains all mandatory sections defined in the configuration, satisfying JAMA output formatting requirements.

    Project:
    """

    # Initialize Config Manager
    config_manager = Config()

    # Initialize Framework Engine
    engine = FrameworkEngine(config_manager)

    # Run the automation
    print("\nStarting Rundeck UI Automation Test Case...")
    engine.start_automation()
    print("\nTest Case Completed Successfully.")

if __name__ == "__main__":
    test_rundeck_ui_automation()