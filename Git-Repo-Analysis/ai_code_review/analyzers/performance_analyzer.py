from .base_analyzer import BaseAnalyzer

class PerformanceAnalyzer(BaseAnalyzer):
    def analyze(self, file_path: str, content: str) -> list[dict]:
        issues = []
        lines = content.splitlines()
        
        loop_stack = [] 
        in_string_block = False
        string_delimiter = None

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue

            # 1. Handle Multiline Strings
            count_double = line.count('"""')
            count_single = line.count("'''")

            if in_string_block:
                # We wait for the specific delimiter to close
                if string_delimiter == '"""':
                    if count_double % 2 == 1:
                        in_string_block = False
                elif string_delimiter == "'''":
                    if count_single % 2 == 1:
                        in_string_block = False
                
                # Loop detection is risky on lines with string delimiters, skipping to be safe
                continue

            else:
                # Check for entry into string block
                if count_double % 2 == 1:
                    in_string_block = True
                    string_delimiter = '"""'
                    # If line starts with loop logic but has a docstring afterwards...
                    # e.g. `for i in range(10): """ doc """`
                    # We skip this for simplicity to avoid false positives in complex strings
                    continue
                elif count_single % 2 == 1:
                    in_string_block = True
                    string_delimiter = "'''"
                    continue
            
            # 2. Simple comment check
            if stripped.startswith("#"):
                continue

            indent = len(line) - len(stripped)
            
            # 3. Clean up inline comments for logic detection
            # "for i in range(10): # comment" -> "for i in range(10):"
            code_part = line.split('#')[0].strip()

            # Manage loop stack: pop loops that have closed based on indentation
            while loop_stack and indent <= loop_stack[-1]:
                loop_stack.pop()

            # 4. Nested Loop Check
            if code_part.startswith("for ") and code_part.endswith(":"):
                if loop_stack:
                    issues.append({
                        "type": "performance",
                        "severity": "high",
                        "message": "Possible nested loop detected (O(n^2) risk)",
                        "line": i + 1
                    })
                
                loop_stack.append(indent)
                
        return issues

