"""
Configuration Settings

This module loads environment variables and defines configuration constants
for the application, including database connections and API keys.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Determine the base directory (root project folder)
# config.py is at: .../git-project-onboarding/app/core/config.py
# We want the DB at: .../sql_app.db (root of workspace)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Database Connection
# Use absolute path to ensure DB is always in the project root regardless of CWD
DEFAULT_DB_PATH = BASE_DIR / "sql_app.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")

# Legacy/Unused Model Path (Kept for compatibility)
LLAMA_MODEL_PATH = os.getenv("LLAMA_MODEL_PATH", "/path/to/local/llama-2")

# GitHub API Configuration
GITHUB_API_URL = os.getenv("GITHUB_API_URL", "https://api.github.com")

# Ollama (LLM) Configuration
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
# Use the smaller 1.5b model to fit in tighter memory constraints (~1.1GB RAM)
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:1.5b")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "300.0"))



