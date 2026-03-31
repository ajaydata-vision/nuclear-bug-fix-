# Evaluator

## Metadata

- id: OR-003
- domain: java-enterprise
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: hibernate, jpa, oneToMany, manyToOne, bidirectional, mappedBy, cascade

## Ground Truth

- root_cause: In a bidirectional @OneToMany / @ManyToOne relationship, the @ManyToOne side (OrderItem.order) owns the FK column (order_id). The @OneToMany(mappedBy=) side is the inverse — it is informational only and does not control the FK. Only adding the item to order.items (inverse side) does not set item.order (owner side). Hibernate writes the FK based on the owner side only. With item.order = null, the FK is NULL or Hibernate issues a redundant UPDATE, causing constraint violations.
- why_it_happens: JPA specification: the mappedBy side of a relationship is not the owner and does not control the database column. Developers must explicitly maintain BOTH sides of a bidirectional relationship — setting the owner side (item.setOrder(order)) is required for correct FK persistence.
- accepted_fix: Set both sides of the relationship. Add a convenience method on Order:
  public void addItem(OrderItem item) { items.add(item); item.setOrder(this); }
  Always use this method instead of directly manipulating the items list.
- rejected_fix_patterns:
  - remove mappedBy and add @JoinColumn to Order.items (makes Order the owner, but bidirectional relationships need mappedBy to avoid duplicate FK columns)
  - set orphanRemoval = true (unrelated to the FK ownership issue)

## Evidence Signals

- strongest_signal: item.setOrder(order) missing in the code; SQL shows order_id=NULL in order_items or a redundant UPDATE setting order_id after INSERT; mappedBy correctly specified on the inverse (Order) side
- strongest_alternative_explanation: CascadeType.ALL causing double persist
- why_alternative_is_wrong: CascadeType.ALL cascades save operations to children — it does not cause duplicate inserts. The duplicate or null FK is caused by the owner side not being set, which is an independent issue from cascade type.

## Scoring Notes

- full_credit_conditions:
  - identifies mappedBy (inverse) side not controlling FK
  - explains that item.setOrder(order) must be called to set owner side
  - proposes addItem() convenience method setting both sides
- partial_credit_conditions:
  - identifies the bidirectional relationship issue but proposes removing mappedBy
- fail_conditions:
  - blames CascadeType.ALL
  - suggests disabling cascade and saving items separately
