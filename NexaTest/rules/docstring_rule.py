from engine.rule_base import Rule

class DocstringRule(Rule):
    id = "DOCSTRING_MISSING"

    def evaluate(self, code: str):
        issues = []
        lines = code.splitlines()

        i = 0
        while i < len(lines):
            stripped = lines[i].strip()

            if stripped.startswith("def "):
                func_name = stripped.split("def ")[1].split("(")[0]
                func_line = i + 1

                # Look at next non-empty line
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1

                if j >= len(lines) or not lines[j].strip().startswith(('"""', "'''")):
                    issues.append({
                        "rule": self.id,
                        "message": f"Function '{func_name}' is missing a docstring",
                        "line": func_line,
                        "severity": "info"
                    })

                i = j
            else:
                i += 1

        return issues
