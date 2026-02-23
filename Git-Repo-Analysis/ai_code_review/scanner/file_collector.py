import pathlib
import sys
import os
from typing import List, Dict

# Add root directory to path to import Config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Config import Config

class FileCollector:
    """
    Filters and categorizes files from a list of file paths.
    """

    SUPPORTED_EXTENSIONS = Config.SUPPORTED_EXTENSIONS

    def __init__(self, files: List[str]):
        """
        Initialize the FileCollector.

        Args:
            files (list[str]): A list of all file paths discovered in the project.
        """
        self.files = files

    def get_code_files(self) -> List[str]:
        """
        Filter files to return only those matching supported extensions.

        Returns:
            list[str]: A list of file paths that are considered code files.
        """
        code_files = []
        for file_path in self.files:
            ext = pathlib.Path(file_path).suffix.lower()
            if ext in self.SUPPORTED_EXTENSIONS:
                code_files.append(file_path)
        return code_files

    def categorize_files(self) -> Dict[str, int]:
        """
        Count files by their extension for supported types.

        Returns:
            dict: A dictionary mapping extension strings (e.g., ".py") to counts.
        """
        counts = {ext: 0 for ext in self.SUPPORTED_EXTENSIONS}
        
        for file_path in self.files:
            ext = pathlib.Path(file_path).suffix.lower()
            if ext in self.SUPPORTED_EXTENSIONS:
                counts[ext] += 1
                
        # Return only found extensions to be cleaner
        result = {k: v for k, v in counts.items() if v > 0}
        return result
