import os
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class ProjectLoader:
    """
    Handles loading and basic validation of the project workspace.
    """

    def __init__(self, project_path: str):
        """
        Initialize the ProjectLoader.

        Args:
            project_path (str): The absolute path to the project folder.
        """
        self.project_path = Path(project_path)

    def validate_project(self) -> bool:
        """
        Validate that the project folder exists and contains files.

        Returns:
            bool: True if valid, False otherwise.
        """
        if not self.project_path.exists():
            logger.error(f"Project path does not exist: {self.project_path}")
            return False
        
        if not self.project_path.is_dir():
            logger.error(f"Project path is not a directory: {self.project_path}")
            return False

        # check if contains at least one file
        has_files = False
        for _, _, files in os.walk(self.project_path):
            if files:
                has_files = True
                break
        
        if not has_files:
            logger.warning(f"Project directory is empty: {self.project_path}")
            return False

        logger.info("Project structure validated successfully.")
        return True

    def get_project_metadata(self) -> dict:
        """
        Extract basic metadata about the project.

        Returns:
            dict: Dictionary containing project path, total file count, and total directory count.
        """
        total_files = 0
        total_dirs = 0

        for root, dirs, files in os.walk(self.project_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
            
            total_dirs += len(dirs)
            total_files += len(files)

        metadata = {
            "project_path": str(self.project_path.absolute()),
            "total_files": total_files,
            "total_dirs": total_dirs
        }
        
        logger.info(f"Project Metadata: {metadata}")
        return metadata
