"""
Configuration and credentials management for Gmail Cleaner.

This module handles configuration settings, environment variables,
and credential management for the Gmail API.
"""

import json
import logging
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


# Role-based email detection constants
ROLE_WORDS = {
    "admin", "info", "support", "sales", "billing", "help", "contact", "office", "jobs",
    "careers", "press", "webmaster", "postmaster", "abuse", "noc", "security", "privacy",
    "legal", "marketing", "newsletter", "newsletters", "news", "team", "hello", "hi",
    "service", "services", "hr", "ops", "accounts", "accounting", "finance", "payroll",
    "partners", "partner", "affiliate", "care", "cs", "cx", "success"
}


@dataclass
class GmailConfig:
    """
    Configuration settings for Gmail Cleaner.
    
    This class holds all the configuration parameters needed
    for Gmail API access and application settings.
    """
    
    # Gmail API settings
    credentials_file: str = "credentials/credentials.json"
    token_file: str = "credentials/token.pickle"
    
    # Default analysis settings
    default_max_emails: Optional[int] = None
    default_batch_size: int = 100
    
    # Output settings
    output_directory: str = "output"
    export_format: str = "json"  # json, csv, excel
    
    # Logging settings
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Cache settings
    enable_cache: bool = True
    cache_directory: str = "cache"
    cache_expiry_hours: int = 24
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dict[str, Any]: Configuration as dictionary.
        """
        return asdict(self)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'GmailConfig':
        """
        Create configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            cls: The class to instantiate
            
        Returns:
            Configuration instance
        """
        return cls(**config_dict)


class ConfigManager:
    """
    Configuration manager for Gmail Cleaner.
    
    This class handles loading and saving configuration from various sources
    including environment variables, configuration files, and defaults.
    """
    
    def __init__(self, config_file: str = "gmail_cleaner_config.json"):
        """
        Initialize the configuration manager.
        
        Args:
            config_file (str): Path to the configuration file.
        """
        self.config_file = config_file
        self.config = GmailConfig()
        self._load_configuration()
    
    def _load_configuration(self) -> None:
        """Load configuration from file and environment variables."""
        # First, load from config file if it exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as file_handle:
                    config_data = json.load(file_handle)
                    self.config = GmailConfig.from_dict(config_data)
                    logger.info(f"Configuration loaded from {self.config_file}")
            except (json.JSONDecodeError, TypeError) as error:
                logger.warning(f"Failed to load config file {self.config_file}: {error}")
        
        # Override with environment variables
        self._load_from_environment()
        
        # Ensure required directories exist
        self._create_directories()
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'GMAIL_CREDENTIALS_FILE': 'credentials_file',
            'GMAIL_TOKEN_FILE': 'token_file',
            'GMAIL_MAX_EMAILS': 'default_max_emails',
            'GMAIL_BATCH_SIZE': 'default_batch_size',
            'GMAIL_OUTPUT_DIR': 'output_directory',
            'GMAIL_EXPORT_FORMAT': 'export_format',
            'GMAIL_LOG_LEVEL': 'log_level',
            'GMAIL_LOG_FILE': 'log_file',
            'GMAIL_ENABLE_CACHE': 'enable_cache',
            'GMAIL_CACHE_DIR': 'cache_directory',
            'GMAIL_CACHE_EXPIRY_HOURS': 'cache_expiry_hours',
        }
        
        for env_var, config_attr in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Type conversion based on attribute type
                current_value = getattr(self.config, config_attr)
                
                if isinstance(current_value, bool):
                    env_value = env_value.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(current_value, int):
                    try:
                        env_value = int(env_value)
                    except ValueError:
                        logger.warning(f"Invalid integer value for {env_var}: {env_value}")
                        continue
                
                setattr(self.config, config_attr, env_value)
                logger.debug(f"Configuration {config_attr} set from environment: {env_value}")
    
    def _create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        directories = [
            self.config.output_directory,
        ]
        
        if self.config.enable_cache:
            directories.append(self.config.cache_directory)
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def save_configuration(self) -> None:
        """
        Save current configuration to file.
        
        Returns:
            None
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as file_handle:
                json.dump(self.config.to_dict(), file_handle, indent=2)
                logger.info(f"Configuration saved to {self.config_file}")
        except OSError as error:
            logger.error(f"Failed to save configuration: {error}")
    
    def get_config(self) -> GmailConfig:
        """
        Get the current configuration.
        
        Returns:
            GmailConfig: Current configuration instance.
        """
        return self.config
    
    def update_config(self, **kwargs) -> None:
        """
        Update configuration parameters.
        
        Args:
            **kwargs: Configuration parameters to update
            
        Returns:
            None
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Configuration {key} updated to: {value}")
            else:
                logger.warning(f"Unknown configuration parameter: {key}")
        
        self._create_directories()
    
    def get_credentials_path(self) -> str:
        """
        Get the full path to the credentials file.
        
        Returns:
            str: Full path to credentials file.
        """
        if os.path.isabs(self.config.credentials_file):
            return self.config.credentials_file
        return os.path.abspath(self.config.credentials_file)
    
    def get_token_path(self) -> str:
        """
        Get the full path to the token file.
        
        Returns:
            str: Full path to token file.
        """
        if os.path.isabs(self.config.token_file):
            return self.config.token_file
        return os.path.abspath(self.config.token_file)
    
    def get_output_path(self, filename: str) -> str:
        """
        Get the full path for an output file.
        
        Args:
            filename: Name of the output file
            
        Returns:
            Full path to output file
        """
        return os.path.join(self.config.output_directory, filename)
    
    def validate_credentials(self) -> bool:
        """
        Validate that required credential files exist.
        
        Returns:
            bool: True if credentials file exists, False otherwise.
        """
        credentials_path = self.get_credentials_path()
        
        if not os.path.exists(credentials_path):
            logger.error(f"Credentials file not found: {credentials_path}")
            return False
        
        try:
            with open(credentials_path, 'r', encoding='utf-8') as file_handle:
                credentials_data = json.load(file_handle)
                
                # Basic validation of credentials structure
                if 'installed' not in credentials_data and 'web' not in credentials_data:
                    logger.error("Invalid credentials file format")
                    return False
                
                logger.info("Credentials file validation successful")
                return True
                
        except (json.JSONDecodeError, OSError) as error:
            logger.error(f"Failed to validate credentials file: {error}")
            return False


def setup_logging(config: GmailConfig, verbose: bool = False) -> None:
    """
    Set up logging based on configuration.
    
    Args:
        config: Configuration containing logging settings
        verbose: Whether to show detailed messages in console
        
    Returns:
        None
    """
    # Set log level based on verbosity
    if verbose:
        log_level = getattr(logging, config.log_level.upper(), logging.INFO)
    else:
        log_level = logging.ERROR  # Only show errors when not verbose
    
    # Always log to file if specified
    logging_config = {
        'level': log_level,
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S'
    }
    
    if config.log_file:
        logging_config['filename'] = config.log_file
        logging_config['filemode'] = 'a'
    
    logging.basicConfig(**logging_config)
    
    # Set up specific loggers
    logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
    logging.getLogger('google.auth').setLevel(logging.WARNING)


def get_default_config_manager() -> ConfigManager:
    """
    Get a default configuration manager instance.
    
    Returns:
        ConfigManager: Default configuration manager.
    """
    return ConfigManager()
