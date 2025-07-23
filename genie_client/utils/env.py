"""Environment variable utilities for Databricks Genie Client."""
import os
from typing import Dict, Optional, Union, Any
from pathlib import Path
from dotenv import load_dotenv

def load_env_vars(env_file: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    Load environment variables from .env file.
    
    Args:
        env_file: Path to .env file. If None, will look for .env in the current
                 directory and parent directories.
    
    Returns:
        Dictionary of environment variables
    """
    # Load environment variables from .env file
    if env_file:
        load_dotenv(env_file)
    else:
        # Try to find .env file in current directory or parent directories
        load_dotenv()
    
    # Common configuration
    config = {
        "databricks_url": os.getenv("DATABRICKS_URL"),
        "workspace_id": os.getenv("WORKSPACE_ID"),
        "default_space_id": os.getenv("DEFAULT_SPACE_ID"),
        "poll_interval": int(os.getenv("POLL_INTERVAL", "5")),
        "poll_timeout": int(os.getenv("POLL_TIMEOUT", "600")),
        "enable_natural_language": os.getenv("ENABLE_NATURAL_LANGUAGE", "False").lower() == "true",
        "model_endpoint_name": os.getenv("MODEL_ENDPOINT_NAME"),
    }
    
    # Check for authentication method
    if os.getenv("AZURE_CLIENT_ID") and os.getenv("AZURE_CLIENT_SECRET") and os.getenv("AZURE_TENANT_ID"):
        # Azure AD authentication
        config.update({
            "auth_type": "azure_ad",
            "client_id": os.getenv("AZURE_CLIENT_ID"),
            "client_secret": os.getenv("AZURE_CLIENT_SECRET"),
            "tenant_id": os.getenv("AZURE_TENANT_ID"),
        })
    elif os.getenv("DATABRICKS_PAT"):
        # Personal Access Token authentication
        config.update({
            "auth_type": "pat",
            "personal_access_token": os.getenv("DATABRICKS_PAT"),
        })
    
    return config

def get_config_from_env() -> Dict[str, Any]:
    """
    Get configuration from environment variables.
    
    Returns:
        Dictionary with configuration values that can be used to initialize
        AzureADGenieClientConfig or PATGenieClientConfig.
    """
    config = load_env_vars()
    
    # Remove auth_type as it's not part of the config classes
    auth_type = config.pop("auth_type", None)
    
    return config
