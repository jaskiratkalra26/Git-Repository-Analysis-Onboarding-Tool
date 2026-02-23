import os
from typing import Dict, List, Any

class DirectoryScanner:
    """
    Scans a directory recursively to collect structure information.
    """

    def __init__(self, project_path: str):
        """
        Initialize the DirectoryScanner.

        Args:
            project_path (str): The root path of the project to scan.
        """
        self.project_path = project_path

    def scan(self) -> Dict[str, Any]:
        """
        Traverse the project folder recursively using os.walk().

        Returns:
            dict: A dictionary containing:
                  - "all_files": List[str] of full file paths
                  - "all_directories": List[str] of full directory paths
                  - "total_files": int
                  - "total_directories": int
        """
        all_files: List[str] = []
        all_directories: List[str] = []

        # Traverse the directory
        for root, dirs, files in os.walk(self.project_path):
            # Add current directories to list
            for d in dirs:
                all_directories.append(os.path.join(root, d))
            
            # Add files to list
            for f in files:
                all_files.append(os.path.join(root, f))

        return {
            "all_files": all_files,
            "all_directories": all_directories,
            "total_files": len(all_files),
            "total_directories": len(all_directories)
        }
