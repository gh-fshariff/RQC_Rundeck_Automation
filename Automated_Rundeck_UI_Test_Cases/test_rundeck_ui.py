import sys
import pytest
from pathlib import Path

# Add the root directory to sys.path so we can import from libraries
TOP_OF_TOOL_PATH = Path(__file__).resolve().parents[1]
sys.path.append(str(TOP_OF_TOOL_PATH))

from libraries.config import Config
from libraries.framework_engine import FrameworkEngine

# Initialize the globally shared engine for the test suite
config_manager = Config()
engine = FrameworkEngine(config_manager)


def test_NEW_failed_login():
    """
    Description:
        Verify the system properly rejects invalid credentials and displays an error banner.

    Prerequisites:
        - Rundeck URL is accessible.

    Test Data:
        - Invalid username and password.

    Steps:
        1) Navigate to the Rundeck Job URL.
            ER: The login page loads successfully.
            Note: This step confirms that the application is reachable and the login interface is functional.
        2) Perform Negative Login Test by entering invalid username and password and submit.
            ER: The system blocks login, an error banner is shown, and evidence is captured.
            Notes: This test ensures that authentication mechanism is secure and informs users when login attempts fail.

    Projects: BI Internal SW Tools
    """
    print("\n--- Executing Test Case: Failed Login ---")
    engine.run_failed_login()


def test_NEW_successful_login():
    """
    Description:
        Verify the system allows access with correct credentials.

    Prerequisites:
        - Valid .env file with RUNDECK_USER and RUNDECK_PWD.

    Test Data:
        - Valid credentials from .env.

    Steps:
        1) Navigate to the Rundeck Job URL.
            ER: The login page loads successfully.
            Note: This step confirms that the application is reachable and the login interface is functional.
        2) Enter valid username and password and submit.
        ER: The login is successful and the user is routed to the job parameter form.
            Notes: This test confirms that authentication mechanism is working correctly with valid credentials.

    Projects: BI Internal SW Tools
    """
    print("\n--- Executing Test Case: Successful Login ---")
    engine.run_successful_login()


def test_NEW_negative_fields():
    """
    Description:
        Verify that missing required text fields, dropdowns, or files actively block job execution.

    Prerequisites:
        - Pre-determined fields configured in data/config.json.

    Test Data:
        - Text fields, Dropdowns, and File Uploads from config.json.

    Steps:
        1) Ensure the user is logged into the Rundeck form.
            ER: The job parameter form is displayed and ready for input.
            Note: This step confirms that the user has successfully navigated to the job parameter form, which is \
            necessary before testing field validation.
        2) For each required field, intentionally leave it blank while populating all other fields.
            ER: Each required field is left empty one at a time, while all other fields are filled with valid data, to \
            isolate the validation of each individual field.
            Notes: This approach ensures that validation mechanism for each required field is tested independently, \
            confirming that the system correctly identifies and blocks execution when any required field is missing.
        3) Click 'Run Job Now'.
            ER: A red validation banner appears preventing execution, and screenshot evidence is captured for each field.
            Notes: This step verifies that the system provides immediate feedback to the user about missing required \
            fields and that it effectively prevents job execution until all required information is provided.

    Projects: BI Internal SW Tools
    """
    print("\n--- Executing Test Case: Negative Field Validation ---")
    engine.run_negative_fields()


def test_NEW_happy_path_and_output():
    """
    Description:
        Verify a valid job executes successfully, completes with 'All Steps OK', and produces output.

    Prerequisites:
        - Pre-determined fields configured in data/config.json.

    Test Data:
        - All required files and texts defined in config.json.

    Steps:
        1) Ensure the user is logged into the Rundeck form.
            ER: The job parameter form is displayed and ready for input.
            Note: This step confirms that the user has successfully navigated to the job parameter form, which is \
            necessary before testing the complete execution flow and output validation.
        2) Fill all required and optional form fields with valid test data.
            ER: All fields are populated correctly without any validation errors.
            Notes: This step ensures that the job is configured with valid inputs, which is essential for testing the \
            successful execution and output generation of the job.
        3) Click 'Run Job Now' and actively monitor node execution.
            ER: The job starts successfully, and real-time logs indicate that each step is executing as expected.
            Notes: Active monitoring of the job execution allows for immediate detection of any issues that may arise \
            during the process, ensuring that the job is progressing towards successful completion.
        4) Wait for the 'All Steps OK' success state and capture final logs.
            ER: The job completes with an 'All Steps OK' status, and the final logs confirm that all steps were \
            executed successfully without any warnings or errors.
            Notes: This step validates that the job has completed its execution successfully, which is a critical \
            prerequisite for verifying the correctness of the output file generated by the job.
        5) Fetch the CSV output file directly using authenticated BIFS headers to bypass UI download bottlenecks.
            ER: The CSV file is downloaded successfully using the API, confirming that the output is accessible and \
            that the authentication mechanism for API access is functioning correctly.
            Notes: Using authenticated API calls to fetch the output file allows for a more efficient and reliable \
            way to access the generated CSV.
        6) Verify Output Format: Read the downloaded CSV and verify against the 'expected_csv_sections' in config.json.
            ER: Job succeeds, output is downloaded, and formatting strictly matches JAMA output requirements.
            Notes: This step ensures that the output generated by the job is not only present but also correctly \
            formatted according to the specified requirements, which is essential for the output to be usable for its \
            intended purpose. Validating the content against expected sections confirms that the job is producing the \
            correct data structure and information as defined in the test configuration.

    Projects: BI Internal SW Tools
    """
    print("\n--- Executing Test Case: Happy Path Execution & Output Validation ---")
    engine.run_happy_path()


if __name__ == "__main__":
    # Use pytest to automatically discover and run all test functions in this file.
    sys.exit(pytest.main(["-v", "-s", __file__]))
