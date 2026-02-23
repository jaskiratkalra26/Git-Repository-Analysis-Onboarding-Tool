import logging
import asyncio
from services.orchestrator_service import OrchestratorService

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the Orchestrator Service
# This service handles all interactions: GitHub, DB, Cloning, Scanning, Analysis, AI
orchestrator = OrchestratorService()

async def authenticate_and_get_repos(token: str):
    """
    Authenticates the token and returns a list of repositories using direct service calls.
    
    Args:
        token (str): The GitHub Personal Access Token.
        
    Returns:
        list: A list of repository dictionaries with metadata.
              Returns None if authentication or fetching fails.
    """
    return await orchestrator.authenticate_and_get_repos(token)

async def generate_and_get_project_data(token: str, github_repo_id: int):
    """
    Retrieves or Generates Project Details using the analysis pipeline.
    
    Args:
        token (str): Authenticated GitHub Token.
        github_repo_id (int): The GitHub ID of the selected repository.
        
    Returns:
        dict: The project details (name, description, features, python_files, analysis_results) 
              or None if failed.
    """
    return await orchestrator.generate_project_report(token, github_repo_id)

if __name__ == "__main__":
    # Test connection
    print("Backend Refactoring Complete: main.py is now using OrchestratorService.")

