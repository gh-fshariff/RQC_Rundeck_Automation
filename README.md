# Rundeck UI Automation Framework

This module provides an automated, data-driven framework to execute UI testing for Rundeck RQC jobs. It automatically performs Negative Testing (verifying required fields block execution when left blank) and Happy Path Testing (submitting a valid job, waiting for 'All Steps OK', and verifying the output download).

## Architecture
This framework is designed to integrate cleanly into `xFramework` test suites:
- **`Automated_Rundeck_UI_Test_Cases/test_rundeck_ui.py`**: The main test runner mapped with JAMA requirement docstrings.
- **`libraries/framework_engine.py`**: The core Playwright engine that interacts with the Rundeck DOM.
- **`data/config.json`**: The central configuration file mapping all text inputs, dropdowns, and file uploads.
- **`data/`**: Directory where required input files (e.g. `SampleSheet.csv`) must be stored.
- **`outputs/`**: Where test evidence (screenshots) and final Happy Path output CSV downloads are saved. Each test run dynamically generates a timestamped subfolder inside here to prevent overlapping test results.

## Setup Instructions
1. Activate your virtual environment.
2. Install requirements: `pip install -r requirements.txt`
3. Install Playwright browsers: `playwright install chromium`
4. Create a `.env` file at the root of the project with your Rundeck credentials:
   ```env
   RUNDECK_USER=your_username
   RUNDECK_PWD=your_password
   ```

## Configuration
Before running, update `data/config.json` with your job URL and input mappings:
- `Tool name`: Name of RQC (e.g., Titan, Phoenix)
- `text_fields`: Required text fields (e.g., "Batch ID": "TEST-01")
- `dropdowns`: Required dropdown selections
- `optional_dropdowns`: Dropdowns only needed for the Happy Path (e.g., BIP directory)
- `input_files`: Files required for upload. Place the physical files inside the `data/` directory.

## Running Tests
To run the test suite:
```bash
python Automated_Rundeck_UI_Test_Cases/test_rundeck_ui.py
```
