Project: Mini Fintech Payment & Order System

Tech Stack
- Python
- Flask
- pytest
- Playwright (planned)
- MySQL / SQLite (planned)

Architecture
services/payment_engine.py
api/app.py
tests/unit
tests/integration
tests/utils/assertions.py

Core Features
- create_user
- process_payment
- refund_payment
- get_balance

API Endpoints
POST /users
POST /payments
POST /refunds
GET /users/<user_id>/balance

Testing
- unit tests for PaymentEngine
- integration tests using Flask test_client
- reusable assertion helpers

Advanced Test Scenarios
- sequential payments
- multiple refunds
- payment → refund → payment flows
- validation failures
- balance consistency checks

Current Phase
API integration tests complete.

Next Phase
Add transaction ledger and DB persistence.