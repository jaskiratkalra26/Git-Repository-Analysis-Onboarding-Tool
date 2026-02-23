import os
import sys
import logging
from typing import List, Dict, Optional
import google.generativeai as genai
from .prompt_builder import PromptBuilder
from dotenv import load_dotenv

# Add root directory to path to import Config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Config import Config

# Load the .env file from the project root
# Go up 4 levels from ai_reviewer.py to get to the project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
env_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

class AIReviewer:
    """
    Manages the AI-powered code review process using Google Gemini.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AIReviewer.

        Args:
            api_key (str, optional): The Gemini API key. If not provided, 
                                     looks for GEMINI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv(Config.ENV_GEMINI_API_KEY)
        self.client = None
        self.model = None
        self.prompt_builder = PromptBuilder()

        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(Config.GEMINI_MODEL_NAME)
                logger.info(f"{Config.GEMINI_MODEL_NAME} model initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {e}")
                self.model = None # Fallback logic will trigger if model is None
        else:
            logger.warning(f"{Config.ENV_GEMINI_API_KEY} not found. Helper will run in fallback mode.")

    def select_top_problem_files(self, analysis_results: List[Dict], top_n: int = Config.AI_TOP_PROBLEM_FILES) -> List[Dict]:
        """
        Selects the top N files with the most issues.
        Only considers files that actually have issues.

        Args:
            analysis_results (List[Dict]): Phase-3 analysis results.
            top_n (int): Number of files to select.

        Returns:
            List[Dict]: The top problematic files.
        """
        # Filter out files with no issues
        problem_files = [res for res in analysis_results if len(res.get("issues", [])) > 0]
        
        # Sort files by number of issues (descending)
        sorted_files = sorted(
            problem_files, 
            key=lambda x: len(x.get("issues", [])), 
            reverse=True
        )
        return sorted_files[:top_n]

    def read_file_safely(self, file_path: str) -> str:
        """
        Reads the first few lines of a file safely.

        Args:
            file_path (str): Path to the file.

        Returns:
            str: File content snippet.
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = []
                for _ in range(Config.MAX_AI_CONTEXT_LINES):
                    line = f.readline()
                    if not line:
                        break
                    lines.append(line)
                return "".join(lines)
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return ""

    def call_gemini(self, prompt: str) -> str:
        """
        Calls the Gemini API with the given prompt.

        Args:
            prompt (str): The prompt text.

        Returns:
            str: The AI's response text.
        """
        if not self.model:
            return self._get_fallback_suggestion()

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return self._get_fallback_suggestion()

    def _get_fallback_suggestion(self) -> str:
        """Returns default suggestions when AI is unavailable."""
        return (
            "AI review skipped. Suggested improvements:\n"
            "- Improve modularity\n"
            "- Add logging\n"
            "- Add unit tests\n"
            "- Improve error handling"
        )

    def generate_ai_review(self, analysis_results: List[Dict], readme_content: str) -> List[Dict]:
        """
        Generates AI reviews for the top problematic files.

        Args:
            analysis_results (List[Dict]): Results from Phase 3.
            readme_content (str): Content of the README.md.

        Returns:
            List[Dict]: List containing file paths and AI suggestions.
        """
        ai_results = []
        
        # 1. Select top problematic files
        top_files = self.select_top_problem_files(analysis_results)
        
        if not top_files:
            logger.info("No files with issues found to review.")
            return []

        # 2. Build project context
        project_context = self.prompt_builder.build_project_context(readme_content)

        # 3. Process each file
        for file_data in top_files:
            file_path = file_data.get("file")
            issues = file_data.get("issues", [])
            
            logger.info(f"Generating AI review for: {file_path}")
            
            # Read code
            file_content = self.read_file_safely(file_path)
            
            # Build prompt
            prompt = self.prompt_builder.build_file_prompt(
                file_path=file_path,
                file_content=file_content,
                issues=issues,
                project_context=project_context
            )
            
            # Call Gemini
            ai_response = self.call_gemini(prompt)
            
            # Store suggestions
            ai_results.append({
                "file": file_path,
                "ai_suggestions": ai_response
            })

        return ai_results
