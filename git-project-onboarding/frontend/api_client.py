import httpx
from typing import Optional, Dict, List, Any
import os
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Base URL configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

def authenticate(token: str) -> Optional[Dict[str, Any]]:
    """
    Authenticates the user with the backend using their GitHub token.
    
    Args:
        token (str): The GitHub Personal Access Token.
        
    Returns:
        Optional[Dict[str, Any]]: User info if successful, None otherwise.
    """
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = httpx.post(f"{API_BASE_URL}/auth/verify-token", headers=headers, json={})
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Authentication failed: {response.text}")
            return None
    except Exception as e:
        logger.error(f"Connection error during authentication: {str(e)}")
        return None

def get_repositories(token: str) -> List[Dict[str, Any]]:
    """
    Fetches the list of repositories for the authenticated user.
    
    Args:
        token (str): The GitHub Personal Access Token.
        
    Returns:
        List[Dict[str, Any]]: A list of repository dictionaries.
    """
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = httpx.get(f"{API_BASE_URL}/repos/", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to fetch repositories: {response.text}")
            return []
    except Exception as e:
        logger.error(f"Error fetching repositories: {str(e)}")
        return []

def get_project_details(token: str, repo_id: int, generate_if_missing: bool = False) -> Optional[Dict[str, Any]]:
    """
    Gets details of a project associated with a repository.
    
    Args:
        token (str): The GitHub Personal Access Token.
        repo_id (int): The local repository ID (not GitHub ID).
        generate_if_missing (bool): If True, calls the generate endpoint to create analysis.
        
    Returns:
        Optional[Dict[str, Any]]: Project details or None.
    """
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        if generate_if_missing:
            # Call generation endpoint (POST) - This creates OR returns existing if logic permits
            # Ideally the backend logic handles "if exists return, else create"
            timeout = httpx.Timeout(300.0, connect=60.0)
            response = httpx.post(
                f"{API_BASE_URL}/projects/generate/{repo_id}", 
                headers=headers,
                timeout=timeout
            )
        else:
            # Call GET endpoint but we need to find project by repo_id
            # NOTE: The current backend might only have GET /projects/{project_id}
            # We need a GET /projects/repo/{repo_id} endpoint or similar.
            # For now, assuming the user will use generate_if_missing=True to fetch/create.
            logger.warning("get_project_details called without generate_if_missing=True. " 
                           "Fetching by repo_id is not fully implemented in this client version.")
            return None
            
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            logger.warning("Project not found.")
            return None
        else:
            logger.error(f"Failed to retrieve project details: {response.text}")
            return None
            
    except httpx.ReadTimeout:
        logger.error("The operation timed out. The server might still be processing.")
        return None
    except Exception as e:
        logger.error(f"Error retrieving project: {str(e)}")
        return None
