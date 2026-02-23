import os
import logging
from services.path_manager import setup_paths

# Setup paths before imports
setup_paths()

try:
    from ai_code_review.core.repo_manager import RepoManager
except ImportError as e:
    logging.warning(f"Could not import RepoManager: {e}")
    RepoManager = None

logger = logging.getLogger(__name__)

class CloneService:
    """
    Manages repository cloning operations.
    Handles errors if cloning module is missing.
    """
    def __init__(self, clone_root="cloned_repos"):
        self.clone_root = os.path.join(os.getcwd(), clone_root)
        self.manager = RepoManager(self.clone_root) if RepoManager else None

    def ensure_cloned(self, repo_url: str, token: str) -> str:
        """
        Clones or updates a repository locally.
        
        Args:
            repo_url (str): The clone URL for the repository.
            token (str): Authentication token.
            
        Returns:
            str: Path to the cloned repository.
        """
        if not self.manager:
            logger.error("RepoManager unavailable. Cannot clone.")
            return None

        try:
            logger.info(f"Cloning repository: {repo_url}")
            repo_path = self.manager.clone_repository(repo_url, token)
            logger.info(f"Repository cloned at: {repo_path}")
            return repo_path
        except Exception as e:
            logger.error(f"Clone failed: {e}")
            raise
