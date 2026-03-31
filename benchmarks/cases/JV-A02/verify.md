# Verification

## Before Fix

1. Call processOrder() with a payment that throws RuntimeException
2. Check DB: order record exists with payment_id = null
3. No rollback occurred despite @Transactional

## After Fix

Option A (separate bean):
1. Extract applyPayment() to PaymentApplicationService bean
2. Inject PaymentApplicationService into OrderService
3. Call paymentApplicationService.applyPayment(order, cart)
4. Trigger same payment failure — order record does NOT appear in DB

Option B (self-injection):
1. Add @Autowired private OrderService self in OrderService
2. Call self.applyPayment(order, cart)
3. Trigger same payment failure — rollback confirmed

## Regression Checks

- Successful payment flow: order created with valid payment_id
- Failed payment: no order record in DB (full rollback)
- Partial failure mid-order: no orphan records
- Add TransactionSynchronizationManager.isActualTransactionActive() log in applyPayment — must return true after fix
