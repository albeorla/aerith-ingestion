import json
import os
from typing import Any, List

from interfaces import DataStorageProtocol, EnvironmentConfigProtocol
from monitoring import MonitoringDashboard


class DataStorage(DataStorageProtocol):
    """Handles saving and loading data to/from JSON and JSONL files."""

    def __init__(
        self, env_config: EnvironmentConfigProtocol, monitor: MonitoringDashboard = None
    ):
        self.logger = env_config.get_logger()
        self.monitor = monitor or MonitoringDashboard()

    def save_json(self, data: Any, path: str) -> bool:
        """Save data to a JSON file."""
        if self.monitor:
            self.monitor.log_request("data_storage")
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as outfile:
                json.dump(data, outfile, indent=4)
            self.logger.info(f"Data successfully saved to: {path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving data to {path}: {e}")
            return False

    def load_json(self, path: str) -> Any:
        """Load data from a JSON file."""
        if self.monitor:
            self.monitor.log_request("data_storage")
        try:
            with open(path, "r") as infile:
                data = json.load(infile)
                self.logger.info(f"Data successfully loaded from: {path}")
                return data
        except FileNotFoundError:
            self.logger.error(f"Error: JSON file not found at: {path}")
            return None
        except json.JSONDecodeError:
            self.logger.error(f"Error: Invalid JSON format in {path}")
            return None
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while loading {path}: {e}")
            return None

    def save_jsonl(self, data_list: List[Any], path: str) -> bool:
        """Save data to a JSONL file."""
        try:
            with open(path, "w") as outfile:
                for item in data_list:
                    if isinstance(item, str):  # Already JSON string
                        outfile.write(item + "\n")
                    else:  # Dict or other object
                        json.dump(item, outfile)
                        outfile.write("\n")
            return True
        except Exception as e:
            self.logger.error(f"Error saving JSONL: {e}")
            return False

    def load_jsonl(self, path: str) -> List[Any]:
        """Load data from a JSONL file."""
        data = []
        try:
            with open(path, "r") as infile:
                for line_number, line in enumerate(infile, 1):
                    try:
                        item = json.loads(line)
                        if item is None:  # Skip null values
                            self.logger.warning(
                                f"Skipping null value on line {line_number} in {path}"
                            )
                            continue
                        data.append(item)
                    except json.JSONDecodeError as e:
                        self.logger.error(
                            f"JSONDecodeError on line {line_number} in {path}: {e}"
                        )
                        self.logger.error(f"Problematic line content: '{line.strip()}'")
                        continue
                self.logger.info(f"Data successfully loaded from JSONL file: {path}")
                return data
        except FileNotFoundError:
            self.logger.warning(
                f"JSONL file not found at: {path}. Returning empty list."
            )
            return []
        except Exception as e:
            self.logger.error(
                f"Unexpected error while loading {path}: {e}. Returning empty list."
            )
            return []
