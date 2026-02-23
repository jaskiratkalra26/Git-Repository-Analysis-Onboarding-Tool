import json
import os
import argparse
from engine.rule_engine import RuleEngine
from rules.naming_rule import NamingConventionRule
from rules.function_length_rule import FunctionLengthRule
from rules.parameter_count_rule import ParameterCountRule
from rules.complexity_rule import ComplexityRule
from rules.docstring_rule import DocstringRule

def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config", "rules_config.json")

    with open(config_path, "r") as f:
        return json.load(f)

def analyze_file(file_path):
    """
    Analyzes a single python file and returns a report dictionary.
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    config = load_config()

    engine = RuleEngine(
        rules=[
            NamingConventionRule(),
            FunctionLengthRule(),
            ParameterCountRule(),
            ComplexityRule(),
            DocstringRule()
        ],
        config=config
    )

    findings = engine.analyze(code)

    report = {
        "file": file_path,
        "summary": {
            "total": len(findings),
            "errors": sum(1 for f in findings if f["severity"] == "error"),
            "warnings": sum(1 for f in findings if f["severity"] == "warning")
        },
        "issues": findings
    }
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    report = analyze_file(args.file)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
