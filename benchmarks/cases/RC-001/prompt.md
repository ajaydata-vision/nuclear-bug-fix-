# RC-001: Shared Counter Loses Increments Under Concurrent Access

## User Prompt

Our counter endpoint should increment a shared in-memory counter by one per
request. In low traffic it works, but under parallel load the final count is
often lower than the number of requests sent. What is the actual bug?

## Context Provided To The Skill

- stack: Go 1.22
- versions: single service, multiple goroutines
- environment: local and CI under concurrent tests
- logs:
  - 100 parallel requests sent
  - expected final value: 100
  - observed final value: 74-93
- code excerpt:

```go
var count int

func increment() {
    count = count + 1
}
```

- reproduction:
  1. Run 100 increments concurrently
  2. Read final counter value
  3. Observe lost increments
