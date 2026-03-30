# Evaluator

## Metadata

- id: MO-004
- domain: frontend
- track: bohrbug-core
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: false
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: react-native, memory, images, OutOfMemoryError, android

## Ground Truth

- root_cause: Full-resolution images are loaded and held in memory for all rendered list items without size constraints or recycling, exhausting heap on limited-RAM devices.
- why_it_happens: FlatList virtualizes the list but images loaded at full resolution consume large amounts of memory. Without explicit width/height constraints matching display size, the full bitmap is decoded and held in memory.
- accepted_fix: Specify image dimensions matching the display size (not full resolution), enable memory cache limits in the image library, and verify FlatList windowSize and maxToRenderPerBatch are configured.
- rejected_fix_patterns:
  - add a try/catch around the image load
  - show error placeholder on crash

## Evidence Signals

- strongest_signal: OutOfMemoryError specifically citing bitmap allocation; only low-RAM devices; crash correlates with scroll depth
- strongest_alternative_explanation: Memory leak in FlatList itself
- why_alternative_is_wrong: FlatList virtualizes correctly; the memory consumption is from the image data itself not list overhead

## Scoring Notes

- full_credit_conditions:
  - identifies full-resolution bitmaps held in memory
  - proposes display-size constraints and cache limits
  - explains FlatList virtualisation vs image memory distinction
- partial_credit_conditions:
  - identifies memory issue but only suggests paginating the list
- fail_conditions:
  - suggests catching the OOM error
  - blames the device for insufficient memory
