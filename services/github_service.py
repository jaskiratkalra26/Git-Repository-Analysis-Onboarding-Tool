import logging
import asyncio
from services.path_manager import setup_paths

# Ensure paths are set up before importing app modules
setup_paths()

try:
    from app.services.github_service import (
        verify_access_token, 
        get_user_repositories, 
        get_repository_details, 
        get_readme_content
    )
except ImportError:
    # Handle cases where import might fail if paths are not correct
    logging.error("Failed to import GitHub services from git-project-onboarding. Ensure the directory structure is correct.")
    # Define stubs to prevent immediate crash, though functionality will be broken
    async def verify_access_token(*args, **kwargs): return None
    async def get_user_repositories(*args, **kwargs): return []
    async def get_repository_details(*args, **kwargs): return {}
    async def get_readme_content(*args, **kwargs): return ""

logger = logging.getLogger(__name__)

class GitHubService:
    """
    Service layer for GitHub API interactions.
    Wraps the existing functional implementation into a class-based service.
    """
    
    async def authenticate_user(self, token: str):
        """Verify the GitHub token and return user details."""
        try:
            return await verify_access_token(token)
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise

    async def get_repositories(self, token: str):
        """Fetch all repositories for the authenticated user."""
        try:
            return await get_user_repositories(token)
        except Exception as e:
            logger.error(f"Failed to fetch repositories: {e}")
            raise

    async def get_repo_details(self, token: str, repo_id: int):
        """Fetch detailed information for a specific repository."""
        try:
            return await get_repository_details(token, repo_id)
        except Exception as e:
            logger.error(f"Failed to fetch details for repo {repo_id}: {e}")
            raise

    async def get_readme(self, token: str, full_name: str) -> str:
        """Fetch README content for a repository."""
        try:
            content = await get_readme_content(token, full_name)
            return content if content else ""
        except Exception as e:
            logger.warning(f"Failed to fetch README for {full_name}: {e}")
            return ""
