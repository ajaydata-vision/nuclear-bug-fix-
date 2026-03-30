# VE-002: Python Package Import Fails Due To Transitive Dependency Version Conflict

## User Prompt

After installing a new package our FastAPI app fails to start with an ImportError on pydantic. Nothing else changed. What is the bug?

## Context Provided To The Skill

- stack: Python 3.11.7, FastAPI 0.110, pydantic 1.10 vs pydantic 2.x conflict
- environment: development after pip install
- logs:
- ImportError: cannot import name 'BaseSettings' from 'pydantic'
  - pip install shows conflicting requirements
  - pydantic 2.x installed but code uses pydantic v1 API
- code excerpt:
```python
from pydantic import BaseSettings  # pydantic v1 API
```
- reproduction:
1. pip install fastapi pydantic-settings
2. Import BaseSettings from pydantic
3. Observe ImportError
