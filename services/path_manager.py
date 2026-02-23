import sys
import os
import logging

logger = logging.getLogger(__name__)

def setup_paths():
    """
    Configures sys.path to include necessary sub-project directories.
    This ensures imports key modules from git-project-onboarding, Git-Repo-Analysis, and NexaTest works.
    """
    project_root = os.getcwd()
    
    paths_to_add = [
        "git-project-onboarding", 
        "Git-Repo-Analysis", 
        "NexaTest",
        "Nexatest--FolderTreeStructure"
    ]
    
    for path in paths_to_add:
        full_path = os.path.join(project_root, path)
        if full_path not in sys.path:
            sys.path.append(full_path)
            # logger.debug(f"Added {full_path} to sys.path")
