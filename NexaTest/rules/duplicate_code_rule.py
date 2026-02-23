from engine.rule_base import Rule
from collections import defaultdict

class DuplicateCodeRule(Rule):
    id = "DUPLICATE_CODE"
    MIN_DUPLICATES = 3

    def configure(self, cfg):
        self.MIN_DUPLICATES = cfg.get("min_duplicates", self.MIN_DUPLICATES)

    def evaluate(self, code: str):
        issues = []
        seen = defaultdict(list)

        for line_no, _, stripped in self.get_lines(code):
            if stripped and not stripped.startswith("#"):
                seen[stripped].append(line_no)

        for text, occurrences in seen.items():
            if len(occurrences) >= self.MIN_DUPLICATES:
                issues.append({
                    "rule": self.id,
                    "message": f"Duplicate line appears {len(occurrences)} times",
                    "line": occurrences[0],
                    "severity": "warning"
                })

        return issues
