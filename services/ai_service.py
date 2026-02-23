import logging
import asyncio
from services.path_manager import setup_paths

# Setup paths
setup_paths()

try:
    from app.services.readme_parser import parser
except ImportError:
    logging.warning("Readme parser failed to import.")
    parser = None

logger = logging.getLogger(__name__)

class AIService:
    """
    Service layer for AI-based operations.
    Wraps README parsing and potentially other LLM tasks.
    """
    
    async def parse_readme(self, content: str) -> dict:
        """
        Parses README content using the Llama model via Ollama.
        
        Args:
            content (str): The markdown content of the README.
            
        Returns:
            dict: Extracted project details (name, description, features).
        """
        if not parser:
            logger.error("Parser unavailable.")
            return {}

        try:
            # Add a timeout to avoid blocking the whole pipeline if LLM is slow/down
            # We use asyncio.wait_for inside here
            extracted_data = await asyncio.wait_for(parser.parse_readme(content), timeout=60.0)
            return extracted_data
        except asyncio.TimeoutError:
            logger.warning("README parsing timed out (Ollama slow/unreachable). Returning empty metadata.")
            return {}
        except Exception as e:
            logger.error(f"Failed to parse README: {e}")
            return {}
