# RC-008: Flaky Test Fails Only In Randomized Order

## User Prompt

One of our Jest tests passes every time when run alone, but fails randomly in
CI when the whole suite runs. The failing assertion says a feature flag is still
enabled even though the test expects the default disabled state. What is the real
bug?

## Context Provided To The Skill

- stack: Node.js 20 + Jest 29
- versions: monorepo test suite
- environment: CI parallel runs and random test ordering
- logs:
  - failing test passes with `jest path/to/test.spec.ts`
  - fails intermittently in full suite
  - another test in same package mutates `global.flags.betaCheckout = true`
- code excerpt:

```ts
beforeAll(() => {
  global.flags = { betaCheckout: false };
});

test('checkout is disabled by default', () => {
  expect(global.flags.betaCheckout).toBe(false);
});
```

- reproduction:
  1. Run suite in random order
  2. Observe intermittent failure
  3. Run the test in isolation
  4. Observe pass
