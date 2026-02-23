from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseAnalyzer(ABC):
    """
    Abstract base class for all code analyzers.
    Enforces a standard analyze method signature.
    """

    @abstractmethod
    def analyze(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """
        Analyze code content and return a list of issues.

        Args:
            file_path (str): The path to the file.
            content (str): The string content of the file.

        Returns:
            list[dict]: A list of dictionary objects representing issues.
                        Each issue should have:
                        {
                            "type": "quality/security/performance",
                            "severity": "low/medium/high",
                            "message": "description",
                            "line": int | None
                        }
        """
        pass
