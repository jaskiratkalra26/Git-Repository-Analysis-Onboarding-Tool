from rules.naming_rule import NamingConventionRule

def test_naming_violation():
    rule = NamingConventionRule()
    issues = rule.evaluate("def BadName():\n    pass")
    assert len(issues) == 1
