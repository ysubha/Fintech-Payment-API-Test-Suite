# Mini Fintech Payment & Order System

A production-style REST API test automation framework built to demonstrate SDET 2 level skills — REST API coverage, schema validation, idempotency testing, unittest.mock, Allure reporting, and GitHub Actions CI/CD.

[![CI](https://github.com/ysubha/mini-fintech-system/actions/workflows/tests.yml/badge.svg)](https://github.com/ysubha/mini-fintech-system/actions/workflows/tests.yml)

---

## Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [API Endpoints](#api-endpoints)
- [Test Pyramid](#test-pyramid)
- [Key Testing Concepts Demonstrated](#key-testing-concepts-demonstrated)
- [How to Run Locally](#how-to-run-locally)
- [How to Run Tests](#how-to-run-tests)
- [CI/CD Pipeline](#cicd-pipeline)
- [Design Decisions](#design-decisions)
- [Known Limitations](#known-limitations)

---

## Project Overview

A Flask-based payment system that supports user creation, payment processing, and refunds — backed by an in-memory engine with optional MySQL persistence. The primary purpose of this project is to demonstrate comprehensive API test automation at SDET 2 level, including:

- Full REST API coverage (happy path, negative, edge cases)
- Contract validation using `jsonschema`
- Idempotency key testing for duplicate payment prevention
- DB layer isolation using `unittest.mock`
- Parametrized test scenarios using `pytest`
- Dynamic test data generation using `Faker`
- End-to-end flow using Playwright API context
- Reporting via Allure
- CI/CD via GitHub Actions

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.14 | Core language |
| Flask | REST API framework |
| pytest | Test runner |
| pytest-xdist | Parallel test execution |
| requests | HTTP client (e2e tests) |
| Playwright | E2E API flow testing |
| Faker | Dynamic test data generation |
| jsonschema | API response contract validation |
| unittest.mock | DB layer isolation |
| Allure | Test reporting |
| GitHub Actions | CI/CD pipeline |
| MySQL | Optional persistence layer |

---

## Architecture

```
┌─────────────────────────────────────────┐
│              HTTP Request               │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│           app.py (Flask API)            │
│  /users  /payments  /refunds  /balance  │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│      payment_engine.py (Business        │
│      Logic + In-Memory State)           │
│  _users{}  _transactions[]              │
└────────────────┬────────────────────────┘
                 │ (try/except — optional)
┌────────────────▼────────────────────────┐
│         db.py (MySQL Persistence)       │
│    USERS table  |  TRANSACTIONS table   │
└─────────────────────────────────────────┘
```

**Key design decision:** The `PaymentEngine` holds state in-memory (`_users` dict, `_transactions` list). DB writes are wrapped in `try/except` — if MySQL is unavailable, the engine continues operating. This makes tests deterministic and DB-independent.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users` | Create a new user with initial balance |
| POST | `/payments` | Process a payment (supports idempotency key) |
| POST | `/refunds` | Refund a payment by transaction ID |
| GET | `/users/<user_id>/balance` | Get current balance for a user |
| GET | `/users/<user_id>/transactions` | Get transaction history for a user |

### Request / Response Shapes

**POST /users**
```json
Request:  { "user_id": "User001", "amount": 1000 }
Response: { "status": "SUCCESS", "balance": 1000.0 }
```

**POST /payments**
```json
Request:  { "user_id": "User001", "amount": 500 }
Headers:  { "Idempotency-Key": "uuid-here" }  (optional)
Response: { "status": "SUCCESS", "balance": 500.0, "txn_id": "TXN_1" }
```

**POST /refunds**
```json
Request:  { "user_id": "User001", "amount": 500, "txn_id": "TXN_1" }
Response: { "status": "SUCCESS", "balance": 1000.0 }
```

**Failure Response (all endpoints)**
```json
{ "status": "FAILED", "reason": "USER_NOT_FOUND" }
```

**Failure Reason Codes**

| Reason | Description |
|--------|-------------|
| `INVALID_INPUT` | Missing required fields |
| `INVALID_AMOUNT` | Negative, zero, null, or non-numeric amount |
| `USER_NOT_FOUND` | User does not exist |
| `USER_ALREADY_EXISTS` | Duplicate user creation |
| `INSUFFICIENT_FUNDS` | Payment exceeds current balance |
| `INVALID_TRANSACTION_ID` | Refund references unknown transaction |
| `PAYMENT_REFUND_COMPLETED` | Refund already processed for this transaction |

---

## Test Pyramid

```
        /\
       /E2E\        1 test  — Playwright API context (requires live server)
      /──────\
     /Integ-  \     35 tests — Flask test_client, real engine, schema validation,
    / ration   \               idempotency, parametrized scenarios
   /────────────\
  /    Unit      \  25 tests — PaymentEngine direct, unittest.mock, edge cases
 /________________\
```

| Layer | Count | Location | Fixture |
|-------|-------|----------|---------|
| Unit | 25 | `tests/unit/` | `pay_engine` |
| Integration | 35 | `tests/integration/` | `server_client` |
| E2E | 1 | `tests/playwright/` | Live server required |

---

## Key Testing Concepts Demonstrated

### 1. Schema Validation (`jsonschema`)
API response structure is validated independently of value assertions. Three schemas enforced:

```python
# Base success schema
{ "type": "object", "properties": { "status": {"type": "string"}, "balance": {"type": "number"} }, "required": ["status", "balance"] }

# Payment success schema (includes txn_id)
{ "type": "object", "properties": { "status": {"type": "string"}, "balance": {"type": "number"}, "txn_id": {"type": "string"} }, "required": ["status", "balance", "txn_id"] }

# Failure schema
{ "type": "object", "properties": { "status": {"type": "string"}, "reason": {"type": "string"} }, "required": ["status", "reason"] }
```

**Why it matters:** Catches type mismatches (e.g., balance returned as string instead of number) that value assertions miss.

### 2. Idempotency Testing
`POST /payments` supports an optional `Idempotency-Key` header. Duplicate requests with the same key return the cached response without reprocessing.

```
Request 1: Idempotency-Key: abc123 → processes payment, returns TXN_1, balance 900
Request 2: Idempotency-Key: abc123 → returns cached response, TXN_1, balance 900 (no double charge)
Request 3: Idempotency-Key: xyz789 → new payment processed, TXN_2, balance 800
```

Three test scenarios:
- Duplicate key returns identical response
- Different keys each process independently
- Same key with different amount still returns first cached response

### 3. DB Isolation with `unittest.mock`
The `PaymentEngine` persists to MySQL inside `try/except` blocks. Two mock tests verify the engine operates correctly when DB is unavailable:

```python
@patch('services.payment_engine.create_user_in_db')
def test_db_failure_on_user_creation_mock(mock_db, pay_engine, fake):
    mock_db.side_effect = Exception('DB is down')
    response = pay_engine.create_user(fake.user_name(), 1000)
    assert response['status'] == 'SUCCESS'  # engine continues despite DB failure
```

**Patch path rule applied:** `services.payment_engine.create_user_in_db` (where used) — not `services.db.create_user_in_db` (where defined).

### 4. Dynamic Test Data with `Faker`
Used in tests where `user_id` value is irrelevant to the assertion outcome (negative cases):

```python
def test_user_creation_missing_amount_failure(server_client, fake):
    user_json = {'user_id': fake.user_name()}  # value irrelevant — test fails on missing amount
    response = server_client.post('/users', json=user_json)
    assert response.status_code == 400
```

### 5. Parametrized Scenarios
```python
@pytest.mark.parametrize('amount', [-200, None, 'abc'])
def test_user_creation_invalid_amount_failure(server_client, fake, amount):
```

### 6. State Validation Pattern
Every mutation test verifies the final state via a separate GET call:
```
POST /payments → assert response balance → GET /balance → assert same balance
```
Prevents false positives from response-only assertions.

---

## How to Run Locally

### Prerequisites
- Python 3.11+
- pip

### Setup

```bash
git clone https://github.com/ysubha/mini-fintech-system.git
cd mini-fintech-system

pip install -r requirements.txt
```

### Configuration

Copy the example config and update if needed:
```bash
cp properties.ini.example properties.ini
```

Default `properties.ini`:
```ini
[API]
base_url = http://127.0.0.1:5000

[SQL]
host = localhost
database = mini_fintech
user = root
password = root
USER_TABLE = USERS
TRANSACTIONS_TABLE = TRANSACTIONS
```

**Note:** MySQL is optional. If unavailable, DB writes are silently skipped and all unit/integration tests still pass.

---

## How to Run Tests

### Run all tests (unit + integration, parallel):
```bash
pytest
```

### Run with specific marker:
```bash
# Unit tests only
pytest tests/unit -v

# Integration tests only
pytest tests/integration -v

# Schema validation tests only
pytest tests/integration/test_schema_validation.py -v

# Idempotency tests only
pytest tests/integration/test_idempotency.py -v
```

### Run E2E tests (requires live server):
```bash
# Terminal 1 — start Flask server
python -m flask --app utils.app:api run --port 5000

# Terminal 2 — run e2e tests
pytest -m e2e -v
```

### Generate Allure report:
```bash
pytest --alluredir=allure-results
allure serve allure-results
```

---

## CI/CD Pipeline

GitHub Actions runs on every push and pull request to `main`.

**Pipeline stages:**
```
checkout → setup Python 3.11 → install dependencies → run pytest (unit + integration) → upload Allure results
```

E2E tests are excluded from CI (`-m "not e2e"`) — they require a live server.

Pipeline config: `.github/workflows/tests.yml`

---

## Design Decisions

**1. In-memory engine as source of truth**
`PaymentEngine` holds state in `_users` dict and `_transactions` list. DB persistence is optional. This keeps tests fast, deterministic, and DB-independent.

**2. `autouse` reset fixture**
```python
@pytest.fixture(autouse=True)
def reset_engine():
    pay_engine.reset()
    try: reset_db()
    except: pass
    yield
```
Every test starts with a clean slate. No test pollution.

**3. xdist parallel execution is safe**
Each pytest-xdist worker spawns a separate process with its own `pay_engine` instance. No shared in-memory state across workers. The only shared resource (MySQL) is handled via `try/except`.

**4. Idempotency at the API layer**
Idempotency key checking lives in `app.py`, not `PaymentEngine`. The engine's job is business logic — idempotency is an API concern.

**5. Patch location for unittest.mock**
Always patch `services.payment_engine.X` (where used), not `services.db.X` (where defined). Patching at the definition site does not affect the already-imported reference.

---

## Known Limitations

- `idempotency_store` in `app.py` is in-memory — resets on server restart. Production systems use Redis or a DB-backed store.
- No `PUT` or `DELETE` endpoints — scope limited to payment flow.
- E2E test requires manual server startup — not integrated into CI.
- MySQL schema setup not scripted — manual DB setup required for persistence layer.
- Refund amount is not validated against original payment amount — a known open item.
