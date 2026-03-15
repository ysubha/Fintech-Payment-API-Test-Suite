'''

1️⃣ Transaction ledger
2️⃣ Database MySQL persistence to PaymentEngine
3️⃣ Playwright UI on API for end-to-end flows
4️⃣ Add concurrency tests (race conditions)
5️⃣ Idempotency keys for payments
observability/logging
UI E2E coverage
'''

'''
UNIT TESTS:
    Group 1 – User Creation : Create user successfully |	User not found | Duplicate user fails | Negative balance fails
    Group 2 – Get Balance : Get balance success | Get balance for non-existent user
    Group 3 – Payments : Successful payment  | Exact balance payment  | Insufficient funds | Negative payment | Zero payment
    Group 4 – Refund : Successful refund | Refund negative amount
    🔥 BONUS (Strong Candidate Move) : Multiple sequential payments reduce balance correctly | Payment then refund restores balance
    
INTEGRATION TESTS:
    Your API tests will verify:
        User APIs        -> Create user | Duplicate user | Invalid balance
        Payment APIs     -> Successful payment | Insufficient funds | Invalid amount | User not found
        Refund APIs      -> Successful refund | Invalid refund amount
        State validation -> After API call → verify balance via API.
'''

'''
APIS:
    POST /users
    POST /payments
    POST /refunds
    GET /users/<user_id>/balance
'''

'''
Engine Result	HTTP Status
SUCCESS	200
INVALID_INPUT	400
USER_NOT_FOUND	404
INSUFFICIENT_FUNDS	409
'''

'''
Phase 1 — Transaction Ledger (NEXT)

Right now payments probably update balance directly.

Real fintech systems never rely on balance mutation.
They rely on a ledger.

Add:

services/
    ledger.py

Ledger entry example:

{
  id
  user_id
  type: PAYMENT | REFUND
  amount
  reference_payment_id
  timestamp
}

Engine change:

balance = sum(all ledger entries)

Why this matters for interviews:

Event sourcing concept

Audit trail

Financial system design

Very SDET-II friendly discussion point.

Phase 2 — Persistence Layer

Add:

repository/
    user_repository.py
    transaction_repository.py

Use either:

SQLite (simpler)

MySQL (more realistic)

Key concept:

Separate business logic from DB

PaymentEngine
    ↓
Repository Layer
    ↓
Database

Interviewers love seeing Repository Pattern.

Phase 3 — Idempotency (VERY IMPORTANT)

Payment APIs must support idempotency keys.

Example:

POST /payments
Idempotency-Key: abc123

If the same request repeats → do not double charge.

Add table:

idempotency_keys

This is very common fintech interview question.

Phase 4 — Concurrency Protection

Simulate:

2 simultaneous payments

Prevent race conditions.

Approaches:

DB transactions

optimistic locking

row locking

You can add tests like:

test_concurrent_payments()
Phase 5 — End-to-End Automation (Playwright)

Once UI is added.

Example:

Create user
Make payment
Verify UI balance
Verify API balance
Verify DB ledger

This demonstrates test pyramid understanding.'''