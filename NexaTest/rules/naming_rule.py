import re
from engine.rule_base import Rule

class NamingConventionRule(Rule):
    id = "NAMING_CONVENTION"

    def evaluate(self, code: str):
        issues = []

        for line_no, _, stripped in self.get_lines(code):
            if stripped.startswith("def "):
                name = stripped.split("def ")[1].split("(")[0]
                if not re.match(r"^[a-z_][a-z0-9_]*$", name):
                    issues.append({
                        "rule": self.id,
                        "message": f"Function '{name}' is not snake_case",
                        "line": line_no,
                        "severity": "warning"
                    })
        return issues
