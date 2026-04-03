# Evaluator

## Metadata

- id: RN-002
- domain: mobile
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: react-native, flatlist, performance, keyExtractor, memoization, re-render

## Ground Truth

- root_cause: The inline `renderItem` arrow function creates a new reference on every parent render. FlatList's internal PureComponent comparison sees a changed prop and re-renders all items. Missing `keyExtractor` is a contributing factor that prevents React from tracking item identity, amplifying the problem.
- why_it_happens: Every parent re-render (caused by `filterOpen` state change) creates a new `({ item }) => <ProductCard product={item} />` arrow function. FlatList receives a new `renderItem` reference each time and cannot skip re-rendering its items. `keyExtractor` missing means React falls back to index-based diffing, which also cannot detect stable items. Both issues compound.
- accepted_fix: Add `keyExtractor={(item) => item.id.toString()}`, memoize renderItem with `useCallback`, and wrap `ProductCard` in `React.memo`.
- rejected_fix_patterns:
  - reduce the number of items in the list
  - add a loading state to delay rendering
  - switch to ScrollView with all items
  - blame the store selector without verifying selector stability

## Evidence Signals

- strongest_signal: All 200 items re-render on state changes unrelated to the products array; no keyExtractor in the code
- strongest_alternative_explanation: The `useProductStore` selector returns a new array reference on every call, causing FlatList to see changed data even when products are unchanged
- why_alternative_is_wrong: The reproducing event is a `filterOpen` state change which does not interact with the store at all. Even if the selector returned a new reference, FlatList re-renders triggered by `filterOpen` changes confirm the unstable `renderItem` reference is the primary driver — no store involvement required. To rule out selector instability: wrap the selector in `shallow` equality (Zustand) and verify re-renders still occur.

## Scoring Notes

- full_credit_conditions:
  - identifies missing keyExtractor as a root cause
  - identifies inline renderItem (unstable reference) as a root cause
  - prescribes keyExtractor + useCallback + React.memo combination
- partial_credit_conditions:
  - identifies only one of the two causes (keyExtractor OR unstable renderItem)
  - recommends React.memo without addressing keyExtractor
- fail_conditions:
  - blames the store or selector
  - recommends reducing item count as the solution
  - suggests switching to ScrollView
