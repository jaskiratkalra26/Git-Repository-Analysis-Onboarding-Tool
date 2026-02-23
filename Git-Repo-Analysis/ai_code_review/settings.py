import os
from pathlib import Path

# Configuration values
DEFAULT_CLONE_DIR = "cloned_repos"
SUPPORTED_PROVIDERS = ["github"]

def get_github_token() -> str | None:
    """
    Retrieves the GitHub token from the environment variable GITHUB_TOKEN.
    
    Returns:
        str | None: The GitHub token if found, otherwise None.
    """
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return None
    return token

def get_clone_dir() -> Path:
    """
    Returns the absolute path to the default clone directory.
    
    Returns:
        Path: Absolute path to the clone directory.
    """
    return Path(os.getcwd()) / DEFAULT_CLONE_DIR
