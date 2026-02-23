from engine.rule_base import Rule

class FunctionLengthRule(Rule):
    id = "FUNCTION_LENGTH"
    MAX_LINES = 50

    def configure(self, cfg):
        self.MAX_LINES = cfg.get("max_lines", self.MAX_LINES)

    def evaluate(self, code: str):
        issues = []
        lines = code.splitlines()

        in_func = False
        func_start = 0
        func_indent = 0
        func_name = ""
        count = 0

        for i, line in enumerate(lines, start=1):
            stripped = line.lstrip()
            indent = len(line) - len(stripped)

            if stripped.startswith("def "):
                in_func = True
                func_start = i
                func_indent = indent
                func_name = stripped.split("def ")[1].split("(")[0]
                count = 0

            elif in_func and indent <= func_indent:
                in_func = False

            if in_func:
                count += 1
                if count > self.MAX_LINES:
                    issues.append({
                        "rule": self.id,
                        "message": f"Function '{func_name}' exceeds {self.MAX_LINES} lines",
                        "line": func_start,
                        "severity": "error"
                    })
                    in_func = False

        return issues
