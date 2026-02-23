import os

class Config:
    """
    Central configuration for the AI Code Review System.
    """
    # -------------------------------------------------------------------------
    # System Configuration
    # -------------------------------------------------------------------------
    DEFAULT_CLONE_DIR = "cloned_repos"
    
    # -------------------------------------------------------------------------
    # Scanner Configuration
    # -------------------------------------------------------------------------
    SUPPORTED_EXTENSIONS = {'.py', '.js', '.java', '.cpp', '.ts'}
    
    # -------------------------------------------------------------------------
    # Analyzer Configuration
    # -------------------------------------------------------------------------
    
    # Quality Analyzer
    MAX_FILE_LINES = 400
    MAX_FUNCTION_PARAMS = 5
    MAX_FUNCTION_LINES = 50
    
    # Security Analyzer
    SECURITY_RISKY_CALLS = [
        "eval(", 
        "exec(", 
        "os.system(", 
        "subprocess.call(", 
        "pickle.load("
    ]
    SECURITY_CREDENTIAL_PATTERNS = [
        "password =", 
        "api_key =", 
        "secret ="
    ]
    
    SECURITY_SAFE_PATTERNS = [
        "os.getenv",
        "os.environ",
        "environ.get",
        "Config."
    ]
    
    # Analysis Engine
    DEEP_CHECK_EXTENSIONS = ('.py',)  # Tuple for startswith/endswith checks
    
    # -------------------------------------------------------------------------
    # AI Engine Configuration
    # -------------------------------------------------------------------------
    GEMINI_MODEL_NAME = "gemini-2.5-flash"
    MAX_AI_CONTEXT_LINES = 400
    AI_TOP_PROBLEM_FILES = 3
    
    # -------------------------------------------------------------------------
    # Environment Variables
    # -------------------------------------------------------------------------
    ENV_GITHUB_TOKEN = "GITHUB_TOKEN"
    ENV_GEMINI_API_KEY = "GEMINI_API_KEY"

    # -------------------------------------------------------------------------
    # Scoring Configuration
    # -------------------------------------------------------------------------
    INITIAL_FILE_SCORE = 100
    ISSUE_PENALTIES = {
        "quality": {
            "low": -1,
            "medium": -3,
            "high": -5
        },
        "security": {
            "low": -2, 
            "medium": -5,
            "high": -10
        },
        "performance": {
            "low": -2,
            "medium": -4,
            "high": -4
        }
    }
