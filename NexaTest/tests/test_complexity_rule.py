from rules.complexity_rule import ComplexityRule

def test_high_complexity():
    code = """
def f():
    if x: pass
    if x: pass
    if x: pass
    if x: pass
    if x: pass
    if x: pass
    if x: pass
    if x: pass
    if x: pass
    if x: pass
    if x: pass
"""
    rule = ComplexityRule()
    issues = rule.evaluate(code)
    assert len(issues) == 1
