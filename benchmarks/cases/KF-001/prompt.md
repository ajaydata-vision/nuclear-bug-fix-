# KF-001: Kafka Consumer Receives No Messages — Partition Assigned But Lag Shows Zero

## User Prompt

We have a Spring Boot service that consumes from a Kafka topic. The producer is
confirmed running and sending messages — we see them in `kafka-console-consumer`
with `--from-beginning`. Our `@KafkaListener` service starts cleanly, logs show
the partition is assigned, but zero messages are ever received. No errors. No
deserialization issues. Just silence. What is wrong?

## Context Provided To The Skill

- stack: Spring Boot 3.2.3, Spring Kafka 3.1.2, Apache Kafka 3.6.1
- versions: Java 17, Docker-based Kafka cluster
- environment: staging, newly created consumer group
- logs:
  - `[INFO] KafkaMessageListenerContainer - partitions assigned: [orders-0, orders-1, orders-2]`
  - `[INFO] KafkaMessageListenerContainer - group id: order-processor-v1`
  - (no `@KafkaListener` method log lines ever appear)
  - `kafka-consumer-groups.sh --describe --group order-processor-v1`:
    ```
    TOPIC     PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG  CONSUMER-ID
    orders    0          1847            1847             0    order-processor-v1-...
    orders    1          923             923              0    order-processor-v1-...
    orders    2          1102            1102             0    order-processor-v1-...
    ```
- code excerpt:
```java
@Service
public class OrderConsumer {

    @KafkaListener(topics = "orders", groupId = "order-processor-v1")
    public void processOrder(String message) {
        log.info("[KAFKA] received: {}", message);
        // process order...
    }
}
```
```yaml
# application.yml — no explicit auto-offset-reset configured
spring:
  kafka:
    bootstrap-servers: kafka:9092
    consumer:
      group-id: order-processor-v1
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.apache.kafka.common.serialization.StringDeserializer
```
- reproduction:
  1. Producer sends 5000 messages to `orders` topic
  2. Start consumer service (first time this group-id has ever connected)
  3. Consumer logs show partitions assigned
  4. Zero messages processed
  5. `kafka-consumer-groups.sh --describe` shows LAG=0 for all partitions
