import os
import logging
import sys
from .quality_analyzer import QualityAnalyzer
from .security_analyzer import SecurityAnalyzer
from .performance_analyzer import PerformanceAnalyzer

# Add root directory to path to import Config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Config import Config

logger = logging.getLogger(__name__)

class AnalysisEngine:
    """
    Central controller for running all analyzers on the codebase.
    """

    def __init__(self):
        """
        Initialize the AnalysisEngine with all available analyzers.
        """
        self.quality_analyzer = QualityAnalyzer()
        self.security_analyzer = SecurityAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()

    def analyze_file(self, file_path: str) -> dict:
        """
        Run relevant analyzers on a single file.

        Args:
            file_path (str): Absolute path to the file.

        Returns:
            dict: { "file": file_path, "issues": [...] }
        """
        issues = []
        try:
            # Use safe file reading as per requirements
            with open(file_path, 'r', encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # 1. Run Security Analyzer (Run on all code files)
            issues.extend(self.security_analyzer.analyze(file_path, content))

            # 2. Run Deep Checks (Quality & Performance)
            if file_path.lower().endswith(Config.DEEP_CHECK_EXTENSIONS):
                issues.extend(self.quality_analyzer.analyze(file_path, content))
                issues.extend(self.performance_analyzer.analyze(file_path, content))

        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")

        return {
            "file": file_path,
            "issues": issues
        }

    def analyze_project(self, code_files: list[str]) -> list[dict]:
        """
        Analyze a list of code files.

        Args:
            code_files (list[str]): List of file paths to analyze.

        Returns:
            list[dict]: List of results for each file.
        """
        results = []
        for file_path in code_files:
            result = self.analyze_file(file_path)
            # Only include files with issues? The prompt output example shows a file with issues.
            # "Return: [ { 'file': '...', 'issues': [...] }, ... ]"
            # It doesn't explicitly say filtered, but usually reports contain all or just issues.
            # The summary counts "Files analyzed", implying we keep all logic or count them.
            # I will return all file results structure as requested.
            results.append(result)
        
        return results
