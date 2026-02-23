from engine.rule_engine import RuleEngine
from rules.naming_rule import NamingConventionRule
from rules.docstring_rule import DocstringRule

def test_engine_multiple_rules():
    code = "def BadName():\n    pass"
    engine = RuleEngine(
        rules=[NamingConventionRule(), DocstringRule()],
        config={
            "NAMING_CONVENTION": {"enabled": True},
            "DOCSTRING_MISSING": {"enabled": True}
        }
    )
    issues = engine.analyze(code)
    assert len(issues) == 2
