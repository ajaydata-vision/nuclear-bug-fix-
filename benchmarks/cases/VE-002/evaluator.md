# Evaluator

## Metadata

- id: VE-002
- domain: version-external-intelligence
- track: regression-version
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: true
- requires_runtime_access: false
- requires_log_access: true
- tags: python, pip, dependency-conflict, importerror, transitive-dependency

## Ground Truth

- root_cause: A newly installed package pulled in pydantic v2 as a transitive dependency. In pydantic v2, BaseSettings was moved to the pydantic-settings package.
- why_it_happens: pydantic v2 is a major version with breaking changes. BaseSettings was extracted into a separate package. Code using pydantic v1 APIs breaks without code changes when v2 is installed.
- accepted_fix: Install pydantic-settings and update the import: from pydantic_settings import BaseSettings. Or pin pydantic to v1: pydantic>=1.0,<2.0
- rejected_fix_patterns:
  - downgrade all packages to resolve the conflict
  - use importlib to conditionally import

## Evidence Signals

- strongest_signal: ImportError citing BaseSettings; pip install shows pydantic 2.x; this is a known breaking change in pydantic v2
- strongest_alternative_explanation: Python version incompatibility
- why_alternative_is_wrong: The error is specifically about BaseSettings location, a documented pydantic v2 breaking change, not Python version

## Scoring Notes

- full_credit_conditions:
  - identifies pydantic v2 moved BaseSettings
  - proposes pydantic-settings install and import update
  - or proposes pinning pydantic<2
- partial_credit_conditions:
  - identifies pydantic version conflict but proposes only pinning without updating imports
- fail_conditions:
  - blames FastAPI bug
  - suggests virtualenv recreation without addressing the root conflict
