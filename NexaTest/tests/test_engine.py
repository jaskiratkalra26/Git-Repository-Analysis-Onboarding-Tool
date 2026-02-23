from engine.rule_engine import RuleEngine
from rules.naming_rule import NamingConventionRule

def test_engine_execution():
    engine = RuleEngine(
        rules=[NamingConventionRule()],
        config={"NAMING_CONVENTION": {"enabled": True}}
    )
    issues = engine.analyze("def BadName():\n    pass")
    assert len(issues) == 1
