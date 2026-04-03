# KF-003: One Kafka Partition Permanently Stuck — Other Partitions Processing Normally

## User Prompt

Our notification Kafka consumer has been running fine for weeks. Yesterday it
stopped processing messages from partition 1. Partitions 0 and 2 are processing
normally. Partition 1's lag is growing at the rate of incoming messages — it is
completely stuck. The consumer is running and healthy. No restarts help. What
is blocking partition 1?

## Context Provided To The Skill

- stack: Spring Boot 3.2.3, Spring Kafka 3.1.2, Apache Kafka 3.6.1
- versions: Java 17
- environment: production
- logs (repeated every 5 seconds for partition 1):
  ```
  [ERROR] ListenerExecutionFailedException: Listener method could not be invoked
  Caused by: org.springframework.kafka.support.converter.ConversionException:
    Failed to convert from [class java.lang.String] to [class com.example.NotificationEvent]
  Caused by: com.fasterxml.jackson.core.JsonParseException:
    Unexpected character ('{' (code 123)) was expected a name
    at [Source: (String)"{{\"type\":\"SMS\",\"to\":\"+91..."; line: 1, column: 2]
  [INFO]  Seeking to current position for [notifications-1@offset 94821]
  [INFO]  Seeking to current position for [notifications-1@offset 94821]
  [INFO]  Seeking to current position for [notifications-1@offset 94821]
  ```
- code excerpt:
```java
@KafkaListener(topics = "notifications", groupId = "notification-sender")
public void sendNotification(NotificationEvent event) {
    // Spring Kafka auto-deserializes String → NotificationEvent via Jackson
    notificationService.send(event);
}
```
```yaml
spring:
  kafka:
    consumer:
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      properties:
        spring.json.trusted.packages: com.example
```
- reproduction:
  1. A producer published a malformed JSON message to notifications partition 1 at offset 94821
  2. Consumer attempts to deserialize, fails with JsonParseException
  3. Spring Kafka retries the same offset indefinitely
  4. Partition 1 is permanently blocked at offset 94821
  5. New valid messages queued behind offset 94821 are also unprocessable
