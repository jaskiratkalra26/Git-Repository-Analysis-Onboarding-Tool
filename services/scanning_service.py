import logging
import asyncio
from pathlib import Path
from typing import Union
from services.path_manager import setup_paths

# Ensure paths before specific module import
setup_paths()

try:
    from ai_code_review.scanner.directory_scanner import DirectoryScanner
    from ai_code_review.scanner.file_collector import FileCollector
except ImportError:
    logging.warning("DirectoryScanner/FileCollector could not be imported.")
    DirectoryScanner = None
    FileCollector = None

try:
    from app.utils.folder_tree.manager import generate_tree_structure_from_path
except ImportError as e:
    logging.warning(f"Failed to import generate_tree_structure_from_path from app.utils.folder_tree.manager: {e}. Falling back to internal stub.")
    def generate_tree_structure_from_path(path: Union[str, Path], limit_depth: int = -1) -> str:
        return f"Tree structure generation failed. Path: {path}"

logger = logging.getLogger(__name__)

class ScanningService:
    """
    Manages scanning of cloned repositories for file discovery.
    """
    
    def get_repository_structure(self, repo_path: Union[str, Path], limit_depth: int = -1) -> str:
        """
        Generates a visual tree structure string from a folder path by delegating to the tree manager.
        """
        return generate_tree_structure_from_path(repo_path, limit_depth)

    def scan_for_python_files(self, repo_path: str):
        """
        Scans a repository path for all .py files.
        """
        if not DirectoryScanner or not FileCollector:
            logger.warning("Scanner components missing. Returning empty list.")
            return []
            
        try:
            ds = DirectoryScanner(repo_path)
            scan_data = ds.scan()
            fc = FileCollector(scan_data["all_files"])
            code_files = fc.get_code_files()
            
            # Filter strictly for python files
            python_files = [f for f in code_files if f.endswith('.py')]
            logger.info(f"Found {len(python_files)} Python files in {repo_path}")
            return python_files
            
        except Exception as e:
            logger.error(f"Scanning failed for {repo_path}: {e}")
            return []
