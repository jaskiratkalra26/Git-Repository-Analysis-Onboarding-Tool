from engine.rule_base import Rule

class ComplexityRule(Rule):
    id = "COMPLEXITY"
    MAX_BRANCHES = 10

    def configure(self, cfg):
        self.MAX_BRANCHES = cfg.get("max_branches", self.MAX_BRANCHES)

    def evaluate(self, code: str):
        issues = []
        branch_keywords = ("if ", "for ", "while ", "elif ", "except ", "case ")

        in_func = False
        func_name = ""
        func_line = 0
        branch_count = 0

        for line_no, line, stripped in self.get_lines(code):
            if stripped.startswith("def "):
                if in_func and branch_count > self.MAX_BRANCHES:
                    issues.append({
                        "rule": self.id,
                        "message": (
                            f"Function '{func_name}' has high branching complexity "
                            f"({branch_count} branches)"
                        ),
                        "line": func_line,
                        "severity": "warning"
                    })

                in_func = True
                func_name = stripped.split("def ")[1].split("(")[0]
                func_line = line_no
                branch_count = 0

            elif in_func:
                for kw in branch_keywords:
                    if stripped.startswith(kw):
                        branch_count += 1

        # Check last function
        if in_func and branch_count > self.MAX_BRANCHES:
            issues.append({
                "rule": self.id,
                "message": (
                    f"Function '{func_name}' has high branching complexity "
                    f"({branch_count} branches)"
                ),
                "line": func_line,
                "severity": "warning"
            })

        return issues
