# Code Review Assistant (CRA) – Phase 1

## Overview
The Code Review Assistant (CRA) is a Python-based, rule-driven static code analysis module designed to assess code quality and maintainability. It focuses on identifying common issues found in both human-written and AI-generated Python code, such as poor readability, excessive complexity, and unnecessary bulkiness.

This module is intended for internal use as a lightweight quality gate within a larger AI-enabled document processing system.

---

## Key Objectives
- Provide a deterministic and explainable static code review mechanism
- Identify maintainability and readability issues early
- Support configurable rule execution without modifying core logic
- Avoid runtime execution or AI-based analysis for reliability and simplicity

---

## Features
- Rule-based static analysis (no code execution)
- Config-driven rule enable/disable and thresholds
- Structured JSON output with summary and detailed findings
- Command-line interface for easy usage
- Designed to detect common AI-generated code patterns

---

## Implemented Rules (Phase 1)

The module implements **seven maintainability-focused rules**:

1. **Naming Convention Rule**  
   Detects non–PEP8-compliant (non-snake_case) function names.

2. **Function Length Rule**  
   Flags functions that exceed a configurable maximum number of lines.

3. **Duplicate Code Rule**  
   Identifies repeated lines of code that indicate copy-paste or AI verbosity.

4. **Parameter Count Rule**  
   Detects functions with too many parameters, indicating over-engineering.

5. **Dead Code Rule**  
   Flags functions that are defined but never used.

6. **Complexity Rule**  
   Detects high branching complexity based on control-flow statements.

7. **Docstring Missing Rule**  
   Identifies functions that do not contain a docstring.

## Configuration

Rule behavior is controlled using a JSON configuration file:
config/rules_config.json

This file allows:
- Enabling or disabling specific rules
- Adjusting rule thresholds (e.g., max function length)

No code changes are required to update rule behavior.

---

## Usage

### Run analysis on a Python file
python run_analysis.py samples/bad_code.py

##Output

The tool produces a structured JSON report containing:

-File name
-Summary of issues by severity
-Detailed list of rule violations

##Testing
Basic unit and integration tests are included.
