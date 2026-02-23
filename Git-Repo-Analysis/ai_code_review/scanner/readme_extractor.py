import os
from typing import Optional

class ReadmeExtractor:
    """
    Locates and reads the README file in a project.
    """

    README_CANDIDATES = ['README.md', 'README.txt', 'readme.md']

    def __init__(self, project_path: str):
        """
        Initialize the ReadmeExtractor.

        Args:
            project_path (str): The root path of the project.
        """
        self.project_path = project_path

    def find_readme(self) -> Optional[str]:
        """
        Search for a README file in the project root.

        Returns:
            str | None: The full path to the README file if found, else None.
        """
        for candidate in self.README_CANDIDATES:
            full_path = os.path.join(self.project_path, candidate)
            if os.path.exists(full_path):
                return full_path
        return None

    def extract_content(self) -> str:
        """
        Read and return the content of the README file safely.

        Returns:
            str: The content of the README file, or empty string if not found or readable.
        """
        readme_path = self.find_readme()
        if not readme_path:
            return ""

        try:
            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except OSError:
            # Handle permission errors or other IO issues
            return ""
