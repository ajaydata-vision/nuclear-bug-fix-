# IN-012: ETL Pipeline Silently Drops Rows Due To Validation Failure

## User Prompt

Our ETL pipeline is losing 15% of rows between source and destination with no errors logged. Where are the rows going?

## Context Provided To The Skill

- stack: Python 3.11, pandas 2.0, PostgreSQL 16.1
- environment: production data pipeline
- logs:
- source has 10000 rows, destination has 8500 rows
  - 1500 rows silently dropped
  - dropped rows have null in 'category' column
  - validation step drops rows where category is not in allowed_categories
  - null not in allowed_categories
- code excerpt:
```python
df = df[df['category'].isin(allowed_categories)]  # drops nulls silently
```
- reproduction:
1. Run ETL with source data containing null category rows
2. Count input vs output rows
3. Observe 1500 missing rows
