from .base_analyzer import BaseAnalyzer
import sys
import os

# Add root directory to path to import Config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Config import Config

class QualityAnalyzer(BaseAnalyzer):
    def analyze(self, file_path: str, content: str) -> list[dict]:
        issues = []
        lines = content.splitlines()

        # A) Large File Check
        if len(lines) > Config.MAX_FILE_LINES:
            issues.append({
                "type": "quality",
                "severity": "medium",
                "message": "File too large, consider splitting into modules",
                "line": None
            })

        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # B) Function Checks
            if stripped.startswith("def ") and stripped.endswith(":"):
                # 1. Parameter Check
                try:
                    # simplistic extraction: assume params are between first ( and last )
                    start_paren = stripped.find('(')
                    end_paren = stripped.rfind(')')
                    if start_paren != -1 and end_paren != -1:
                        params_str = stripped[start_paren+1:end_paren]
                        # Count parameters by splitting logic
                        if params_str.strip():
                            # naive counting by comma
                            # Note: this fails on defaults with commas e.g. func(a=[1,2])
                            # But per "Keep logic simple", this is acceptable for now.
                            param_count = params_str.count(',') + 1
                            if param_count > Config.MAX_FUNCTION_PARAMS:
                                issues.append({
                                    "type": "quality",
                                    "severity": "medium",
                                    "message": "Too many parameters, consider using an object",
                                    "line": i + 1
                                })
                except Exception:
                    pass

                # 2. Docstring Check & 3. Function Length
                # Determine indentation of the def line
                def_indent = len(line) - len(line.lstrip())
                
                # Look ahead for Docstring and Length
                func_length = 0
                has_docstring = False
                
                # Check for docstring in immediate next non-empty lines
                # We also calculate length here by iterating until indentation drops
                
                body_start_index = i + 1
                found_body = False
                
                for j in range(i + 1, len(lines)):
                    sub_line = lines[j]
                    sub_stripped = sub_line.strip()
                    
                    if not sub_stripped:
                        continue # Skip empty lines for indentation check? 
                                 # Usually empty lines are part of function but don't break scope
                    
                    sub_indent = len(sub_line) - len(sub_line.lstrip())
                    
                    if sub_indent <= def_indent:
                        # End of function
                        break
                    
                    # Inside function
                    func_length += 1
                    
                    # Check first body line for docstring
                    if not found_body:
                        found_body = True
                        if sub_stripped.startswith('"""') or sub_stripped.startswith("'''"):
                            has_docstring = True
                
                # Add implicit length of the def line? The prompt says "If function length > 50 lines".
                # Usually means total lines. 
                # Let's count from `def` to end.
                total_func_lines = (j if j < len(lines) else len(lines)) - i
                # Or just use the counted body lines? "Function too long".
                # Let's use total lines spanned.
                
                if total_func_lines > Config.MAX_FUNCTION_LINES:
                    issues.append({
                        "type": "quality",
                        "severity": "medium",
                        "message": "Function too long, consider refactoring",
                        "line": i + 1
                    })

                if not has_docstring:
                    issues.append({
                        "type": "quality",
                        "severity": "low", # Prompt didn't specify severity, guessing Low or Medium. 
                        # Requirement: "message: Missing docstring for function"
                        # I'll use low as it's less critical.
                        "message": "Missing docstring for function",
                        "line": i + 1
                    })

        return issues

