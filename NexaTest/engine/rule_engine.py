class RuleEngine:
    def __init__(self, rules, config):
        self.rules = rules
        self.config = config

    def analyze(self, code: str):
        findings = []

        for rule in self.rules:
            cfg = self.config.get(rule.id, {})
            if not cfg.get("enabled", True):
                continue

            if hasattr(rule, "configure"):
                rule.configure(cfg)

            try:
                findings.extend(rule.evaluate(code))
            except Exception as e:
                findings.append({
                    "rule": rule.id,
                    "message": f"Rule failed safely: {str(e)}",
                    "line": None,
                    "severity": "info"
                })

        return findings
