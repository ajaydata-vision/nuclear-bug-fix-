# Verification

## Before Fix
- Consumer logs show partitions assigned, zero messages processed
- kafka-consumer-groups.sh: CURRENT-OFFSET = LOG-END-OFFSET, LAG = 0

## After Fix
1. Add to `application.yml`:
   ```yaml
   spring:
     kafka:
       consumer:
         auto-offset-reset: earliest
   ```
2. **Stop the consumer service first** — `--reset-offsets` requires the group to have no active members:
   ```bash
   # Stop the Spring Boot service, then:
   kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
     --group order-processor-v1 \
     --reset-offsets --to-earliest \
     --topic orders --execute
   # Expected output: orders  0  0  (offset reset to 0)
   #                  orders  1  0
   #                  orders  2  0
   ```
3. Restart consumer service
4. kafka-consumer-groups.sh: LAG now shows total number of historical messages
5. `[KAFKA] received: ...` log lines appear, LAG decreases toward 0

## Regression Checks
- New messages produced after consumer starts: processed normally (earliest applies only at first join with no committed offset)
- Consumer restart mid-processing: resumes from last committed offset, not from beginning
- Different topic: verify auto-offset-reset=earliest applies to all listeners in this service
