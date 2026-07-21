# Mini Fintech Payment & Order System

A production-style REST API test-automation framework built to demonstrate SDET-2 level skills - REST API coverage, schema/contract validation, idempotency testing, `unittest.mock` DB isolation, Allure reporting.

---

## Table of Contents

- [Why This Project Exists](#why-this-project-exists)
- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Architecture](#architecture)
- [API Endpoints](#api-endpoints)
- [Test Pyramid](#test-pyramid)
- [Key Testing Concepts Demonstrated](#key-testing-concepts-demonstrated)
- [Concepts Index (jump table)](#concepts-index-jump-table)
- [How to Run Locally](#how-to-run-locally)
- [How to Run Tests](#how-to-run-tests)
- [CI/CD Pipeline](#cicd-pipeline)
- [Design Decisions](#design-decisions)
- [Known Limitations & Open Items](#known-limitations--open-items)

---

## Why This Project Exists

This repo is a deliberately small **system under test** (a Flask payment API) wrapped in a **deliberately thorough test suite**. The API itself is not the point — it is a realistic target that lets the test framework exercise the things a payment/fintech backend actually cares about: money not being lost, no double-charges, contract stability, and correct behaviour when the database is down.

Read it as : *"a compact but honest demonstration of how I design an API test framework end to end — from unit-level business logic, through integration against a real HTTP client, up to a single E2E happy path, all running in CI."*

---

## Project Overview

A Flask-based payment system supporting user creation, payment processing, and refunds — backed by an in-memory engine with **optional** MySQL persistence. The primary purpose is to demonstrate comprehensive API test automation at SDET-2 level, including:

- Full REST API coverage (happy path, negative, edge cases)
- Contract validation using `jsonschema`
- Idempotency-key testing for duplicate-payment prevention
- DB-layer isolation using `unittest.mock`
- Parametrized test scenarios using `pytest`
- Dynamic test data generation using `Faker`
- End-to-end flow using Playwright's API request context
- Reporting via Allure
- CI/CD via GitHub Actions

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.11+ | Core language (CI runs 3.11 — see note below) |
| Flask | REST API framework |
| pytest | Test runner |
| pytest-xdist | Parallel test execution |
| Playwright (sync API) | E2E flow via `playwright.request.new_context()` |
| Faker | Dynamic test data generation |
| jsonschema | API response contract validation |
| unittest.mock | DB-layer isolation |
| Allure | Test reporting |
| GitHub Actions | CI/CD pipeline |
| MySQL (`mysql-connector`) | Optional persistence layer |
| `requests` | Declared HTTP-client dependency *(see note)* |

> **Version note:** CI and the local-setup steps both target **Python 3.11**. Keep the whole doc on one version — if you run a newer interpreter locally, say so explicitly, because `datetime.utcnow()` (used in the engine) is deprecated from 3.12 onward.
>
> **`requests` note:** The E2E test uses **Playwright's `APIRequestContext`**, not the `requests` library. If `requests` is not imported anywhere in the codebase, drop it from this table so the stack matches the code exactly.

---

## Repository Structure

```
mini-fintech-system/
├── services/
│   ├── payment_engine.py      # Core business logic + in-memory state (source of truth)
│   └── db.py                  # SQL persistence layer (optional; INSERT/DELETE only)
├── utils/
│   ├── app.py                 # Flask app: routes, request parsing, idempotency store
│   ├── helper.py              # get_properties() — reads config from properties.ini
│   ├── integration_tests_assertions.py   # Reusable assert_* helpers for API-level tests
│   └── unit_tests_assertions.py          # Reusable assert_* helpers for engine-level tests
├── tests/
│   ├── conftest.py            # Fixtures: pay_engine, fake, server_client, create_user,
│   │                          #           reset_engine (autouse) — clean slate per test
│   ├── constants.py           # DEFAULT_USER_ID, DEFAULT_INITIAL_BALANCE
│   ├── unit/                  # PaymentEngine tested directly (no HTTP)
│   │   ├── test_payment_engine_create_user.py
│   │   ├── test_pay_engine_process_payment.py
│   │   ├── test_payment_engine_receive_refund.py
│   │   ├── test_pay_engine_get_balance.py
│   │   └── test_payment_engine_db_mock.py     # unittest.mock — DB-down resilience
│   ├── integration/           # Flask test_client → real engine over HTTP
│   │   ├── test_create_user_api.py
│   │   ├── test_payments_api.py
│   │   ├── test_refunds_api.py
│   │   ├── test_idempotency.py
│   │   └── test_schema_validation.py          # jsonschema contract checks
│   └── playwright/
│       └── test_payment_flow.py               # 1 E2E happy path (live server required)
├── properties.ini(.example)   # [API] base_url, [SQL] host/db/user/password/tables
├── requirements.txt
├── .github/workflows/tests.yml
└── README.md
```

**How the packages depend on each other (import direction):**

- `tests/*` → import fixtures/helpers from `utils/*` and `tests/constants`, and the system under test from `services/*` and `utils/app`.
- `utils/app.py` → owns the singleton `pay_engine = PaymentEngine()` and the HTTP layer, calling into `services/payment_engine`.
- `services/payment_engine.py` → calls `services/db.py` **inside `try/except`**, so a DB failure never breaks the engine.
- `services/db.py` and `utils/helper.py` → read config via `get_properties()` from `properties.ini`.

> **Structure critique worth knowing:** test-assertion helpers live under `utils/` alongside application utilities (`app.py`, `helper.py`). Cleaner would be a dedicated `tests/utils/` or `tests/asserts/` package so "app code" and "test code" don't share a namespace. Small, but it's the kind of thing a reviewer notices.

---

## Architecture

```
┌─────────────────────────────────────────┐
│              HTTP Request               │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│        utils/app.py (Flask API)         │
│  /users  /payments  /refunds  /balance  │
│  + idempotency store (in-memory)        │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│  services/payment_engine.py (Business   │
│  Logic + In-Memory State)               │
│  _users{}  _transactions[]              │
└────────────────┬────────────────────────┘
                 │ (try/except — optional)
┌────────────────▼────────────────────────┐
│      services/db.py (MySQL)             │
│    USERS table  |  TRANSACTIONS table   │
└─────────────────────────────────────────┘
```

**Key design decision:** `PaymentEngine` holds state in-memory (`_users` dict, `_transactions` list). DB writes are wrapped in `try/except` — if MySQL is unavailable, the engine continues operating. This makes tests deterministic and DB-independent.

---

## API Endpoints

| Method | Endpoint | Description | Tested by |
|--------|----------|-------------|-----------|
| POST | `/users` | Create a new user with initial balance | unit + integration |
| POST | `/payments` | Process a payment (supports idempotency key) | unit + integration + idempotency |
| POST | `/refunds` | Refund a payment by transaction ID | unit + integration |
| GET | `/users/<user_id>/balance` | Get current balance for a user | E2E only |
| GET | `/users/<user_id>/transactions` | Get transaction history for a user | **not currently tested** |

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

| Reason | Emitted by | Covered by a test? |
|--------|-----------|--------------------|
| `INVALID_INPUT` | API layer (missing fields) | ✅ |
| `INVALID_AMOUNT` | engine (negative/zero/null/non-numeric) | ✅ |
| `USER_NOT_FOUND` | engine | ✅ |
| `USER_ALREADY_EXISTS` | engine (duplicate create) | ✅ |
| `INSUFFICIENT_FUNDS` | engine (payment > balance) | ✅ |
| `INVALID_TRANSACTION_ID` | engine (refund of unknown txn) | ❌ **implemented, untested** |
| `PAYMENT_REFUND_COMPLETED` | engine (double refund of same txn) | ❌ **implemented, untested** |

> Two refund guard rails exist in `payment_engine.refund_payment()` but have **no test asserting them**. These are the cheapest, highest-signal tests to add next.

---

## Test Pyramid

```
        /\
       /E2E\        1 test  — Playwright API context (requires live server)
      /──────\
     /Integ-  \     35 cases — Flask test_client, real engine, schema validation,
    / ration   \              idempotency, parametrized scenarios
   /────────────\
  /    Unit      \  25 cases — PaymentEngine direct, unittest.mock, edge cases
 /________________\
```

| Layer | Test functions | Collected cases | Location | Primary fixture |
|-------|----------------|-----------------|----------|-----------------|
| Unit | 16 | 25 | `tests/unit/` | `pay_engine` |
| Integration | 26 | 35 | `tests/integration/` | `server_client` |
| E2E | 1 | 1 | `tests/playwright/` | live server |
| **Total** | **43** | **61** | | |

> **Why two numbers?** 43 test *functions* expand to 61 *collected cases* through `@pytest.mark.parametrize`. Quote **61** as the suite size and **43** as the function count — being able to explain the gap (parametrization) is itself a talking point.

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

**Why it matters:** catches type/contract mismatches (e.g. `balance` returned as a string) that value assertions miss.

### 2. Idempotency Testing
`POST /payments` accepts an optional `Idempotency-Key` header. Duplicate requests with the same key return the cached response without reprocessing.

```
Request 1: Idempotency-Key: abc123 → processes payment, TXN_1, balance 900
Request 2: Idempotency-Key: abc123 → cached response, TXN_1, balance 900 (no double charge)
Request 3: Idempotency-Key: xyz789 → new payment, TXN_2, balance 800
```

Three scenarios covered:
- Same key returns identical response.
- Different keys each process independently (distinct `txn_id`).
- Same key with a **different amount** still returns the first cached response.

### 3. DB Isolation with `unittest.mock`
`PaymentEngine` persists to MySQL inside `try/except`. Two mock tests verify the engine keeps working when the DB is unavailable:

```python
@patch('services.payment_engine.create_user_in_db')
def test_db_failure_on_user_creation_mock(mock_db, pay_engine, fake):
    mock_db.side_effect = Exception('DB is down')
    response = pay_engine.create_user(fake.user_name(), 1000)
    assert response['status'] == 'SUCCESS'  # engine continues despite DB failure
```

**Patch-location rule applied:** patch `services.payment_engine.create_user_in_db` (where the name is *used*), not `services.db.create_user_in_db` (where it is *defined*). Patching the definition site would not affect the already-imported reference.

### 4. Dynamic Test Data with `Faker`
Used where the `user_id` value is irrelevant to the assertion (negative cases):

```python
def test_user_creation_missing_amount_failure(server_client, fake):
    user_json = {'user_id': fake.user_name()}   # value irrelevant — fails on missing amount
    response = server_client.post('/users', json=user_json)
    assert response.status_code == 400
```

### 5. Parametrized Scenarios
```python
@pytest.mark.parametrize('amount', [-200, None, 'abc'])
def test_user_creation_invalid_amount_failure(server_client, fake, amount):
    ...
```

### 6. State Validation Pattern
Every mutation test re-reads state via a separate call rather than trusting the mutating response alone:
```
POST /payments → assert response balance → GET /balance → assert same balance
```
Prevents false positives from response-only assertions.

### 7. Clean-slate isolation (`autouse` reset)
```python
@pytest.fixture(autouse=True)
def reset_engine():
    pay_engine.reset()      # clears the app's singleton engine
    try: reset_db()         # best-effort MySQL wipe
    except Exception: pass
    yield
```
Every test starts from an empty engine — no test pollution, order-independent.

---

## Concepts Index (jump table)

| I want to talk about… | Look at |
|------------------------|---------|
| REST API negative/edge coverage | `tests/integration/test_payments_api.py`, `test_refunds_api.py` |
| Contract / schema testing | `tests/integration/test_schema_validation.py` |
| Idempotency | `tests/integration/test_idempotency.py` + engine `txn` recording |
| Mock / patch-location | `tests/unit/test_payment_engine_db_mock.py` |
| Fixtures & isolation | `tests/conftest.py` |
| Business logic & guard rails | `services/payment_engine.py` |
| Persistence & the try/except boundary | `services/db.py` + engine call sites |
| E2E flow | `tests/playwright/test_payment_flow.py` |

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

**Note:** MySQL is optional. If unavailable, DB writes are silently skipped and all unit/integration tests still pass. Credentials here are plaintext demo values — see *Known Limitations*.

---

## How to Run Tests

```bash
# All tests (unit + integration, parallel via xdist)
pytest

# By layer
pytest tests/unit -v
pytest tests/integration -v

# Focused
pytest tests/integration/test_schema_validation.py -v
pytest tests/integration/test_idempotency.py -v

# E2E (requires a live server)
python -m flask --app utils.app:api run --port 5000   # terminal 1
pytest -m e2e -v                                       # terminal 2

# Allure report
pytest --alluredir=allure-results
allure serve allure-results
```

---

## CI/CD Pipeline

GitHub Actions runs on every push and pull request to `main`.

```
checkout → setup Python 3.11 → install deps → run pytest (unit + integration) → upload Allure results
```

E2E tests are excluded from CI (`-m "not e2e"`) because they need a live server.
Pipeline config: `.github/workflows/tests.yml`.

---

## Design Decisions

**1. In-memory engine as source of truth.** State lives in `_users` / `_transactions`; DB is optional. Keeps tests fast, deterministic, DB-independent.

**2. `autouse` reset fixture.** Clean slate per test; no pollution.

**3. xdist parallelism is process-based.** Each worker is a separate process with its own engine instance, so in-memory state never crosses workers. *This holds because MySQL is effectively off in CI* — see the limitation on shared-DB parallelism below.

**4. Idempotency at the API layer.** The key check lives in `app.py`, not the engine. The engine does business logic; idempotency is an HTTP concern.

**5. Patch where used, not where defined.** `services.payment_engine.X`, never `services.db.X`.

**6. Asymmetric amount rules (intentional).** User creation allows a `0` balance (`amount < 0` is invalid); payments reject `0` (`amount <= 0` is invalid). Different business meaning, deliberately different guards.

---

## Known Limitations & Open Items

- **In-memory / DB divergence (no atomicity).** The engine mutates in-memory state *first*, then writes to the DB inside `try/except`. If the DB write fails, memory reports SUCCESS while the DB has no row — the two silently diverge. There is no outbox/compensation/2-phase pattern. Acceptable for a demo; a real payment system would not tolerate it.
- **Idempotency store is in-memory** (`app.py`) — resets on restart, no TTL/expiry. Production uses Redis or a DB-backed store.
- **Two refund reason codes are untested** — `INVALID_TRANSACTION_ID` and `PAYMENT_REFUND_COMPLETED` are implemented but have no asserting test.
- **`/users/<id>/transactions` endpoint is untested.**
- **Refund amount is not validated against the original payment** — partial/over-refund is possible.
- **No concurrency guards on the in-memory dicts.** Fine on the default single-threaded dev server; unsafe if run threaded.
- **Shared-DB parallelism is unsafe if MySQL is enabled** — `reset_db()` does a `DELETE FROM` in an autouse fixture, so parallel workers sharing one database would wipe each other's rows. Safe today only because CI runs DB-independent.
- **`datetime.utcnow()` is deprecated** from Python 3.12+; prefer `datetime.now(datetime.UTC)`.
- **Plaintext DB credentials in `properties.ini`** — no `.env`/secrets management.
- **Manual MySQL schema setup** — no migrations (Alembic/Flyway) and no seed script.
- **No `PUT`/`DELETE` endpoints** — scope limited to the payment flow.
- **E2E is not in CI** — requires manual server startup.
