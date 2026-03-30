# IN-001: Webhook Never Arrives Because External Service Points To Old URL

## User Prompt

Stripe webhooks stopped arriving after we migrated our API to a new domain. Stripe says events are being sent successfully. What is wrong?

## Context Provided To The Skill

- stack: Node.js 20.11, Stripe webhooks
- environment: production after URL migration
- logs:
- no webhook events received after domain migration
  - Stripe dashboard shows events sending successfully
  - Stripe shows delivery to old domain api.old.example.com
  - new domain is api.new.example.com
- code excerpt:
```
# Stripe webhook endpoint configured in dashboard:
# api.old.example.com/webhooks/stripe
```
- reproduction:
1. Complete a payment
2. Observe Stripe event sent but not received
3. Check Stripe dashboard — delivery URL is old domain
