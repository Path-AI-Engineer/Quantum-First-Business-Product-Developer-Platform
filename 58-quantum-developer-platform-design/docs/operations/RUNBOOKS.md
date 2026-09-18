# Operations runbooks

## Unknown provider outcome

Stop automatic submission, inspect the submission ledger using correlation ID, query the provider when configured, and transition only through `UNKNOWN_RECONCILIATION_REQUIRED`. Never create a replacement external submission without an operator decision.

## Webhook outage

Retain the logical event ID, create bounded delivery attempts with new delivery IDs, apply exponential backoff with jitter, move the exhausted delivery to DLQ, and permit audited manual replay. Consumers must deduplicate by event ID.

## Artifact integrity failure

Block download, preserve the stored digest and audit context, quarantine the object, and rebuild only from immutable job evidence. Do not silently replace content under an existing artifact ID.

## Credential concern

Revoke first, rotate to a new one-time secret, inspect last-used and audit records, and never echo the raw secret into logs or support tickets.

