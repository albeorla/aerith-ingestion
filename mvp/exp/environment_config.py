import os
from typing import Any, Dict

import pandas as pd
from dotenv import load_dotenv
from interfaces import EnvironmentConfigProtocol, LoggerProtocol


class EnvironmentConfig(EnvironmentConfigProtocol):
    """Handles environment variable configuration for the application."""

    # Environment variable keys and their secrecy status
    ENV_VARS = {
        "TODOIST_API_TOKEN": {"key": "TODOIST_API_TOKEN", "secret": True},
        "GOOGLE_API_KEY": {"key": "GOOGLE_API_KEY", "secret": True},
        "GEMINI_MODEL_NAME": {"key": "GEMINI_MODEL_NAME", "secret": False},
        "GEMINI_TEMPERATURE": {"key": "GEMINI_TEMPERATURE", "secret": False},
        "GEMINI_TOP_P": {"key": "GEMINI_TOP_P", "secret": False},
        "GEMINI_TOP_K": {"key": "GEMINI_TOP_K", "secret": False},
        "GEMINI_MAX_OUTPUT_TOKENS": {
            "key": "GEMINI_MAX_OUTPUT_TOKENS",
            "secret": False,
        },
    }

    # Default values for Gemini configuration with refined settings
    GEMINI_DEFAULTS = {
        "model_name": "gemini-2.0-flash-thinking-exp",
        "temperature": 0.3,  # Lowered for more deterministic outputs
        "top_p": 0.9,  # Slightly reduced for more focused token sampling
        "top_k": 50,  # Reduced to limit token consideration for categorization
        "max_output_tokens": 128,  # Reduced to align with expected short JSON responses
    }

    def __init__(self, logger: LoggerProtocol):
        self.logger = logger

        # Load .env file and override system environment variables
        load_dotenv(override=True)
        self.logger.info(f"Current working directory: {os.getcwd()}")

    # logger getter
    def get_logger(self) -> LoggerProtocol:
        return self.logger

    def _get_env_var(self, var_name: str, default: str = "") -> str:
        """Retrieve an environment variable without obfuscation."""
        var_config = self.ENV_VARS.get(var_name, {})
        value = os.getenv(var_config.get("key", ""), default)
        if value == default:
            self.logger.info(
                f"Environment variable '{var_name}' not set. Using default: {default}"
            )
        else:
            self.logger.info(f"Environment variable '{var_name}' found. Value: {value}")
        return value

    def _obfuscate_value(self, value: str) -> str:
        """Obfuscate a value for logging purposes."""
        if value and len(value) > 8:
            return value[:4] + "****" + value[-4:]
        return "****" if value else ""

    def get_env_var_for_display(self, var_name: str, default: str = "") -> str:
        """Retrieve an environment variable, obfuscating if marked as secret."""
        value = self._get_env_var(var_name, default)
        var_config = self.ENV_VARS.get(var_name, {})
        if var_config.get("secret", False) and value:
            return self._obfuscate_value(value)
        return value

    def get_todoist_api_token(self) -> str:
        """Retrieve the Todoist API token from the environment."""
        return self._get_env_var("TODOIST_API_TOKEN", "")

    def get_google_api_key(self) -> str:
        """Retrieve the Google API key from the environment."""
        return self._get_env_var("GOOGLE_API_KEY", "")

    def get_gemini_model_name(self) -> str:
        """Retrieve the Gemini model name from the environment, or use the default."""
        model_name = self._get_env_var(
            "GEMINI_MODEL_NAME",
            self.GEMINI_DEFAULTS["model_name"],
        )
        if not model_name.strip():
            self.logger.warning(
                f"Invalid or empty value for 'GEMINI_MODEL_NAME'. Using default: {self.GEMINI_DEFAULTS['model_name']}"
            )
            model_name = self.GEMINI_DEFAULTS["model_name"]
        self.logger.info(f"Using Gemini model: {model_name}")
        return model_name

    def get_gemini_generation_config(self) -> dict:
        """Retrieve the Gemini generation configuration from the environment, or use defaults."""
        try:
            config = {
                "temperature": self._validate_env_var(
                    "GEMINI_TEMPERATURE",
                    self.GEMINI_DEFAULTS["temperature"],
                    float,
                ),
                "top_p": self._validate_env_var(
                    "GEMINI_TOP_P",
                    self.GEMINI_DEFAULTS["top_p"],
                    float,
                ),
                "top_k": self._validate_env_var(
                    "GEMINI_TOP_K",
                    self.GEMINI_DEFAULTS["top_k"],
                    int,
                ),
                "max_output_tokens": self._validate_env_var(
                    "GEMINI_MAX_OUTPUT_TOKENS",
                    self.GEMINI_DEFAULTS["max_output_tokens"],
                    int,
                ),
            }
            self.logger.info(f"Gemini generation configuration: {config}")
            return config
        except ValueError as e:
            self.logger.error(f"Error parsing Gemini generation config: {e}")
            self.logger.info("Using default configuration values")
            return self.GEMINI_DEFAULTS

    def get_gemini_safety_settings(self) -> Dict[str, Any]:
        """
        Retrieve safety settings for the Gemini API.
        Modify this method based on the actual safety requirements.
        """
        # Example safety settings
        return {
            "safety_level": "standard",
            "filtering": True,
            "adversarial_protection": True,
        }

    def _validate_env_var(
        self, var_name: str, default: Any, expected_type: type
    ) -> Any:
        """
        Validate and retrieve an environment variable. If invalid, use the default.

        Args:
            var_name (str): The name of the environment variable.
            default (Any): The default value to use if the variable is invalid.
            expected_type (type): The expected type of the variable.

        Returns:
            Any: The validated value or the default.
        """
        value = self._get_env_var(var_name, str(default))
        try:
            return expected_type(value)
        except (ValueError, TypeError):
            self.logger.warning(
                f"Invalid value for '{var_name}': {value}. Using default: {default}"
            )
            return default

    def to_dict(self) -> dict:
        """
        Collect all environment configuration values by calling getter methods.
        Uses obfuscated values for display.
        """
        return {
            var_name: self.get_env_var_for_display(var_name)
            for var_name in self.ENV_VARS
        }

    def to_dataframe(self, vertical: bool = False) -> pd.DataFrame:
        """
        Convert the environment configuration values to a pandas DataFrame.

        Args:
            vertical (bool): If True, return the DataFrame in a vertical format (key-value pairs).

        Returns:
            pd.DataFrame: A DataFrame containing the environment configuration values.
        """
        config_dict = self.to_dict()  # Uses obfuscated values
        df = pd.DataFrame([config_dict])
        return df.transpose() if vertical else df

    def get_config_as_str(self, vertical: bool = True, spacing: int = 30) -> str:
        """
        Generate the environment configuration values as a formatted string.

        Args:
            vertical (bool): If True, format the configuration in a vertical format.
            spacing (int): The spacing (column width) for the output.

        Returns:
            str: The formatted string containing the environment configuration.
        """
        config_dict = {
            "TODOIST_API_TOKEN": self.get_env_var_for_display("TODOIST_API_TOKEN"),
            "GOOGLE_API_KEY": self.get_env_var_for_display("GOOGLE_API_KEY"),
            "GEMINI_MODEL_NAME": self.get_gemini_model_name(),
            "GEMINI_TEMPERATURE": self.get_gemini_generation_config()["temperature"],
            "GEMINI_TOP_P": self.get_gemini_generation_config()["top_p"],
            "GEMINI_TOP_K": self.get_gemini_generation_config()["top_k"],
            "GEMINI_MAX_OUTPUT_TOKENS": self.get_gemini_generation_config()[
                "max_output_tokens"
            ],
        }
        log = "\n" + "=" * 30 + "\n"
        log += "\n=== Relevant Environment Configuration ===\n"
        for key, value in config_dict.items():
            log += f"{key:<{spacing}}: {value}\n"
        log += "=" * 30 + "\n"
        return log
