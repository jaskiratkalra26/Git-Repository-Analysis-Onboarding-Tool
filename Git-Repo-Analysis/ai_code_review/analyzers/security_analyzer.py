from .base_analyzer import BaseAnalyzer
import sys
import os

# Add root directory to path to import Config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Config import Config

class SecurityAnalyzer(BaseAnalyzer):
    def analyze(self, file_path: str, content: str) -> list[dict]:
        issues = []
        lines = content.splitlines()
        
        risky_calls = Config.SECURITY_RISKY_CALLS
        
        credential_patterns = Config.SECURITY_CREDENTIAL_PATTERNS
        safe_patterns = Config.SECURITY_SAFE_PATTERNS

        for i, line in enumerate(lines):
            # Check for risky function calls
            for call in risky_calls:
                if call in line:
                    issues.append({
                        "type": "security",
                        "severity": "high",
                        "message": f"{call.replace('(', '()')} usage detected",
                        "line": i + 1
                    })

            # Check for credentials
            for cred in credential_patterns:
                if cred in line: # Simple substring check
                    # Check if the line contains any safe patterns (e.g. env var retrieval)
                    is_safe = False
                    for safe in safe_patterns:
                        if safe in line:
                            is_safe = True
                            break
                    
                    if not is_safe:
                        issues.append({
                            "type": "security",
                            "severity": "high",
                            "message": "Potential hardcoded credential detected",
                            "line": i + 1
                        })
                    
        return issues

