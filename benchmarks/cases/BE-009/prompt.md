# BE-009: Unique Constraint Race Under Concurrent Inserts

## User Prompt

We create a `users` row only if the email does not exist. It works in normal
traffic but under load we sometimes get `duplicate key value violates unique constraint users_email_key`.
Why does the pre-check not protect us?

## Context Provided To The Skill

- stack: Python 3.11.7 + FastAPI 0.110 + PostgreSQL 16.2
- versions: SQLAlchemy 2.0.28
- environment: concurrent API traffic
- logs:
  - two signup requests with same email start within the same second
  - both pass the existence check
  - one insert fails on unique constraint
- code excerpt:

```python
existing = session.query(User).filter_by(email=email).first()
if existing is None:
    user = User(email=email)
    session.add(user)
    session.commit()
```

- reproduction:
  1. Fire two signup requests for the same email concurrently
  2. Observe one request fails with unique constraint violation
