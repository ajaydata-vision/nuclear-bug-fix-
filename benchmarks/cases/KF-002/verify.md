# Verification

## Before Fix
- Consumer processes some messages then rebalances
- Same message processed twice (duplicate payment records)
- "Revoked/Assigned partitions" cycles in logs every 47+ seconds

## After Fix
```yaml
spring:
  kafka:
    consumer:
      max-poll-records: 1        # process one at a time for slow operations
      properties:
        max.poll.interval.ms: 120000  # 2 minutes — safely exceeds 47s worst case
    listener:
      ack-mode: record           # commit after each message, not after batch
```
```java
// Add idempotency check to handle already-stored duplicates:
public void processPayment(ConsumerRecord<String, String> record) {
    if (paymentRepository.existsByPaymentId(record.key())) {
        log.warn("[KAFKA] duplicate detected, skipping: {}", record.key());
        return;
    }
    fraudCheckService.verify(record.value());
    paymentRepository.save(parsePayment(record.value()));
}
```
1. No more "Revoked partitions" cycles during normal processing
2. No duplicate payment records for subsequent messages
3. Existing duplicate records handled by deduplication logic

## Regression Checks
- Fast messages (< 1s): processed normally, no rebalance
- Fraud-check timeout (60s): single message processed, offset committed, no rebalance
- Consumer restart mid-processing: resumes from last per-record commit, no duplication
