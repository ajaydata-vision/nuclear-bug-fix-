# KF-002: Kafka Consumer Rebalance Storm — Partitions Constantly Revoked And Reassigned

## User Prompt

Our Kafka payment event consumer processes some messages successfully, then stops
for 30-60 seconds, then starts again, then stops. The logs are full of
"Revoked partitions" and "Assigned partitions" cycling. Payment events are being
processed twice — we have duplicate payment records in the database. The consumer
never crashes. What is happening?

## Context Provided To The Skill

- stack: Spring Boot 3.2.3, Spring Kafka 3.1.2, Apache Kafka 3.6.1
- versions: Java 17
- environment: production, single consumer instance
- logs (excerpt — repeating pattern):
  ```
  [INFO]  Assigned partitions: [payments-0, payments-1]
  [INFO]  [KAFKA] processing payment: PMT-10041 started
  [INFO]  [KAFKA] calling fraud-check API for PMT-10041 (external, slow)
  [INFO]  [KAFKA] processing payment: PMT-10041 completed (47 seconds)
  [WARN]  Synchronization KafkaResourceHolder registered  after transaction already completed
  [INFO]  Revoked partitions: [payments-0, payments-1]
  [INFO]  Assigned partitions: [payments-0, payments-1]
  [INFO]  [KAFKA] processing payment: PMT-10041 started   ← duplicate!
  ```
- code excerpt:
```java
@KafkaListener(topics = "payments", groupId = "payment-processor")
public void processPayment(ConsumerRecord<String, String> record) {
    log.info("[KAFKA] processing payment: {} started", record.key());
    fraudCheckService.verify(record.value()); // synchronous HTTP call, 30-60s
    paymentRepository.save(parsePayment(record.value()));
    log.info("[KAFKA] processing payment: {} completed ({} seconds)", 
             record.key(), processingTime);
}
```
```yaml
spring:
  kafka:
    consumer:
      group-id: payment-processor
      max-poll-records: 50
      properties:
        max.poll.interval.ms: 30000   # 30 seconds — set by ops team for fast rebalance detection
    listener:
      ack-mode: batch
```
- reproduction:
  1. Produce a batch of payment events where fraud-check takes 45+ seconds each
  2. Consumer processes first message (takes 47s)
  3. Logs show rebalance triggered during processing
  4. Same message processed again after reassignment
