import re
from engine.rule_base import Rule

class DeadCodeRule(Rule):
    id = "DEAD_CODE"

    def evaluate(self, code: str):
        defined = {}
        used = set()

        for line_no, line, stripped in self.get_lines(code):
            if stripped.startswith("def "):
                name = stripped.split("def ")[1].split("(")[0]
                defined[name] = line_no
            elif not stripped.startswith("def "):
                matches = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\(", stripped)
                used.update(matches)

        issues = []
        for name, line_no in defined.items():
            if name not in used:
                issues.append({
                    "rule": self.id,
                    "message": f"Function '{name}' is defined but never used",
                    "line": line_no,
                    "severity": "warning"
                })

        return issues
