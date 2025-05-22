import json
from pathlib import Path
import typing

class ConfigManager:
    """Manages configurations for Tor instances."""

    def __init__(self, config_dir: typing.Optional[Path] = None):
        """
        Initializes the ConfigManager.

        Ensures the configuration directory exists and loads existing configurations
        from the configuration file.

        Args:
            config_dir (Path, optional): Path to the configuration directory.
                                         Defaults to Path.home() / ".config" / "xtor".
        """
        if config_dir is None:
            self.config_dir: Path = Path.home() / ".config" / "xtor"
        else:
            self.config_dir = config_dir
            
        self.config_file_path: Path = self.config_dir / "instances.json"

        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            # Handle potential errors during directory creation, e.g., permission issues
            print(f"Error creating config directory {self.config_dir}: {e}")
            # Depending on desired behavior, could re-raise or exit
        
        self.configs: dict = self._load_all_configs_from_file()

    def _load_all_configs_from_file(self) -> dict:
        """
        Loads all configurations from the JSON file.

        Handles FileNotFoundError and JSONDecodeError gracefully.

        Returns:
            dict: A dictionary of configurations, or an empty dictionary if
                  the file is not found or is corrupted.
        """
        try:
            with open(self.config_file_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            # Log error or handle as appropriate for the application
            print(f"Error decoding JSON from {self.config_file_path}. Starting with empty configuration.")
            return {}
        except Exception as e:
            print(f"An unexpected error occurred while loading {self.config_file_path}: {e}")
            return {}


    def _save_all_configs_to_file(self) -> None:
        """
        Saves all current configurations to the JSON file.

        Configurations are pretty-printed for readability.
        """
        try:
            with open(self.config_file_path, "w") as f:
                json.dump(self.configs, f, indent=4)
        except Exception as e:
            # Handle potential errors during file writing, e.g., permission issues
            print(f"Error saving configs to {self.config_file_path}: {e}")
            # Depending on desired behavior, could re-raise or exit


    def save_config(self, instance_id: str, config_data: dict) -> None:
        """
        Saves a configuration for a given instance ID.

        Args:
            instance_id (str): The unique identifier for the Tor instance.
            config_data (dict): A dictionary containing the configuration
                                parameters for the instance (e.g., host, port).
        """
        if not isinstance(instance_id, str):
            raise ValueError("instance_id must be a string.")
        if not isinstance(config_data, dict):
            raise ValueError("config_data must be a dictionary.")
            
        self.configs[instance_id] = config_data
        self._save_all_configs_to_file()

    def load_config(self, instance_id: str) -> typing.Optional[dict]:
        """
        Loads the configuration for a specific instance ID.

        Args:
            instance_id (str): The unique identifier for the Tor instance.

        Returns:
            dict | None: The configuration dictionary if found, otherwise None.
        """
        return self.configs.get(instance_id)

    def delete_config(self, instance_id: str) -> bool:
        """
        Deletes the configuration for a specific instance ID.

        Args:
            instance_id (str): The unique identifier for the Tor instance.

        Returns:
            bool: True if the configuration was deleted, False otherwise.
        """
        if instance_id in self.configs:
            del self.configs[instance_id]
            self._save_all_configs_to_file()
            return True
        return False

    def list_configs(self) -> dict:
        """
        Lists all currently stored configurations.

        Returns:
            dict: A copy of all configurations.
        """
        return self.configs.copy()

    def get_config_file_path(self) -> str:
        """
        Returns the absolute path to the configuration file.

        Returns:
            str: The configuration file path.
        """
        return str(self.config_file_path.resolve())
