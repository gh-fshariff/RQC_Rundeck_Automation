import os
import json
from dotenv import load_dotenv


class Config:
    def __init__(self):
        # Base folder is one level up from the 'libraries' folder
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.DATA_DIR = os.path.join(self.BASE_DIR, "data")
        self.OUTPUT_DIR = os.path.join(self.BASE_DIR, "outputs")

        # In the new structure, input files are directly in data/
        self.INPUT_DIR = self.DATA_DIR
        self.CONFIG_JSON_PATH = os.path.join(self.DATA_DIR, "config.json")

        # Ensure outputs exists
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

        # Load .env (assuming .env is in the BASE_DIR)
        dotenv_path = os.path.join(self.BASE_DIR, ".env")
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path=dotenv_path)

        self.RUNDECK_USER = os.getenv("RUNDECK_USER")
        self.RUNDECK_PWD = os.getenv("RUNDECK_PWD")

        if not self.RUNDECK_USER or not self.RUNDECK_PWD:
            raise ValueError("RUNDECK_USER or RUNDECK_PWD is not set in the .env file")

    def get_input_data(self):
        if not os.path.exists(self.CONFIG_JSON_PATH):
            raise FileNotFoundError(f"Missing configuration file at {self.CONFIG_JSON_PATH}")
        with open(self.CONFIG_JSON_PATH, "r") as f:
            data = json.load(f)

        tool_name = data.get("tool_name", "").strip().replace(" ", "_")
        tool_version = data.get("tool_version", "").strip().replace(" ", "_")

        if tool_name:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            if tool_version:
                self.OUTPUT_DIR = os.path.join(self.OUTPUT_DIR, tool_name, tool_version, timestamp)
            else:
                self.OUTPUT_DIR = os.path.join(self.OUTPUT_DIR, tool_name, timestamp)
            os.makedirs(self.OUTPUT_DIR, exist_ok=True)

        return data