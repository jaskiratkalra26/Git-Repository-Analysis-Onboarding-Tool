from engine.rule_base import Rule

class ParameterCountRule(Rule):
    id = "PARAMETER_COUNT"
    MAX_PARAMS = 5

    def configure(self, cfg):
        self.MAX_PARAMS = cfg.get("max_params", self.MAX_PARAMS)

    def evaluate(self, code: str):
        issues = []

        for line_no, _, stripped in self.get_lines(code):
            if stripped.startswith("def "):
                signature = stripped.split("def ")[1].split(")")[0]
                params = signature.split("(")[1]
                if params.strip():
                    count = len(params.split(","))
                    if count > self.MAX_PARAMS:
                        name = signature.split("(")[0]
                        issues.append({
                            "rule": self.id,
                            "message": f"Function '{name}' has {count} parameters",
                            "line": line_no,
                            "severity": "warning"
                        })

        return issues
