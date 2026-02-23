import os
import git
import logging
from pathlib import Path
from urllib.parse import urlparse

# Configure logging
logger = logging.getLogger(__name__)

class RepoManager:
    """
    Manages repository cloning and authentication.
    """

    def __init__(self, clone_base_dir: str):
        """
        Initialize the RepoManager.

        Args:
            clone_base_dir (str): Base directory where repositories will be cloned.
        """
        self.clone_base_dir = Path(clone_base_dir)
        self._ensure_base_dir()

    def _ensure_base_dir(self):
        """Ensure the base clone directory exists."""
        try:
            self.clone_base_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Clone base directory ensuring: {self.clone_base_dir}")
        except OSError as e:
            logger.error(f"Failed to create clone directory: {e}")
            raise

    def _format_repo_url(self, repo_url: str, token: str | None) -> str:
        """
        Format the repository URL with the token for authentication if provided.
        
        Behavior:
        - If token is None or empty: return repo_url as-is
        - If token exists AND repo_url starts with "https://github.com":
          convert to: https://<token>@github.com/username/repo.git
        - If repo_url is already SSH (git@github.com:...) do NOT modify

        Args:
            repo_url (str): The original repository URL.
            token (str | None): GitHub token for authentication.

        Returns:
            str: Modified URL with token if applicable.
        """
        if not token:
            return repo_url
        
        # Check for SSH style URL
        if repo_url.startswith("git@"):
            return repo_url
        
        parsed_url = urlparse(repo_url)
        if "github.com" in parsed_url.netloc and parsed_url.scheme == "https":
            # Insert token into the URL
            # Format: https://<token>@github.com/user/repo.git
            new_netloc = f"{token}@{parsed_url.netloc}"
            modified_url = parsed_url._replace(netloc=new_netloc).geturl()
            return modified_url
        
        return repo_url

    def get_repo_name(self, repo_url: str) -> str:
        """
        Extract repository name from the URL.

        Args:
            repo_url (str): The repository URL.

        Returns:
            str: The name of the repository.
        """
        path = urlparse(repo_url).path
        name = path.split('/')[-1]
        if name.endswith('.git'):
            name = name[:-4]
        return name

    def clone_repository(self, repo_url: str, token: str | None = None) -> str:
        """
        Clone the repository into the clone base directory.

        Args:
            repo_url (str): The URL of the repository to clone.
            token (str | None): Optional GitHub token for authentication.

        Returns:
            str: Absolute path to the cloned project folder.
            
        Raises:
            Exception: If cloning fails due to network, auth, or invalid URL.
        """
        repo_name = self.get_repo_name(repo_url)
        target_path = self.clone_base_dir / repo_name
        
        if target_path.exists() and target_path.is_dir():
            # Check if it's already a git repo or just a folder
            if (target_path / ".git").exists():
                logger.info(f"Repository already exists locally at {target_path}. Skipping clone.")
                return str(target_path.absolute())
            else:
                logger.warning(f"Folder {target_path} exists but is not a git repository.")

        formatted_url = self._format_repo_url(repo_url, token)
        
        # Logging based on authentication method
        if token and formatted_url != repo_url:
            masked_url = formatted_url.replace(token, "******")
            logger.info(f"Cloning private repository using token from {masked_url}...")
        else:
            logger.info(f"Cloning public repository (or no token provided) from {repo_url}...")

        try:
            logger.info("Attempting to clone repository... (shallow clone)")
            git.Repo.clone_from(formatted_url, target_path, depth=1)
            logger.info("Clone successful.")
            return str(target_path.absolute())
        except git.GitCommandError as e:
            error_message = str(e).lower()
            if "authentication failed" in error_message or "403" in error_message or "401" in error_message:
                if not token:
                    logger.error("Authentication failed. Repository may be private. Provide a GitHub token.")
                    raise Exception("Cloning failed: Authentication required. The repository might be private.")
                else:
                    logger.error("Authentication failed even with token. Check if the token is valid.")
            
            logger.error(f"Git command failed: {e}")
            raise Exception(f"Failed to clone repository: Git error - {e}")
        except Exception as e:
            logger.error(f"Unexpected error during cloning: {e}")
            raise Exception(f"Failed to clone repository: {e}")
