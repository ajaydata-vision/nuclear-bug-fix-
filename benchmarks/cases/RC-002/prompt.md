# RC-002: Inventory Oversell From Check-Then-Update Logic

## User Prompt

Our checkout flow checks if inventory is available before decrementing it. Under
concurrent orders we sometimes sell the last item twice. The code looks correct
when read top to bottom. Why is it still broken?

## Context Provided To The Skill

- stack: Python 3.11 + PostgreSQL 16
- versions: SQLAlchemy 2.x
- environment: concurrent order placement
- logs:
  - stock count starts at 1
  - two checkout requests arrive almost simultaneously
  - both see `count > 0`
  - final stock is `-1` or duplicate orders are accepted
- code excerpt:

```python
stock = session.execute(text("SELECT count FROM inventory WHERE sku=:sku"), {"sku": sku}).scalar_one()
if stock > 0:
    session.execute(text("UPDATE inventory SET count = count - 1 WHERE sku=:sku"), {"sku": sku})
    session.commit()
```

- reproduction:
  1. Set inventory count to 1
  2. Run two checkouts concurrently
  3. Observe oversell
