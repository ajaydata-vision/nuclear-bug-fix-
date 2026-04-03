# Verification

## Before Fix
- Partition 1 stuck at offset 94821 indefinitely
- "Seeking to current position for [notifications-1@offset 94821]" every 5 seconds
- Partition 1 lag growing; partitions 0 and 2 normal

## After Fix (two steps)

### Step 1 — Immediate recovery (skip the poison pill):
```bash
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group notification-sender \
  --reset-offsets --to-offset 94822 \
  --topic notifications:1 --execute
```
Partition 1 resumes processing from offset 94822.

### Step 2 — Permanent fix (prevent future poison pills from blocking):
```yaml
spring:
  kafka:
    consumer:
      value-deserializer: org.springframework.kafka.support.serializer.ErrorHandlingDeserializer
      properties:
        spring.deserializer.value.delegate.class: org.springframework.kafka.support.serializer.JsonDeserializer
        spring.json.trusted.packages: com.example
```
```java
@KafkaListener(topics = "notifications", groupId = "notification-sender")
public void sendNotification(ConsumerRecord<String, NotificationEvent> record) {
    // Check for deserialization failure header
    if (record.headers().lastHeader(SerializationUtils.DESERIALIZER_EXCEPTION_HEADER) != null) {
        log.error("[KAFKA] poison pill at offset={} partition={}, routing to DLQ",
                  record.offset(), record.partition());
        dlqTemplate.send("notifications.DLQ", record.key(), record.value());
        return;
    }
    notificationService.send(record.value());
}
```

## Regression Checks
- Valid messages on partition 1 after offset 94822: processed normally
- New malformed message on any partition: routed to DLQ, processing continues
- Consumer restart: no re-blocking (ErrorHandlingDeserializer handles it cleanly)
