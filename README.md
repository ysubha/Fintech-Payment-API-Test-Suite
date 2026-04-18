# Payment API Test Suite

REST API test suite for fintech payment flows — 
initiation, validation, status, and error handling.

## Stack
- Python, pytest, requests
- MySQL (transaction state validation)
- Page Object Model structure

## Structure
services/    → API service classes  
tests/       → Test files  
utils/       → Config and helpers  
conftest.py  → Fixtures  

## How to Run
pip install -r requirements.txt
pytest tests/
