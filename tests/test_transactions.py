from datetime import date

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


@pytest.fixture
def deposit_transaction():
    return {
        "amount": 10.5,
        "type": "deposit",
        "date": date.today().strftime("%Y-%m-%d"),
    }


def test_hello():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_get_transactions():
    response = client.get("users/1/transactions")
    assert response.status_code == 200
    for transaction in response.json():
        assert transaction["user_id"] == 1


def test_get_existing_transaction():
    response = client.get("users/1/transactions/1")
    assert response.status_code == 200
    transaction = response.json()
    assert transaction["user_id"] == 1
    assert transaction["id"] == 1


def test_get_nonexisting_transaction():
    response = client.get("users/1/transactions/9999")
    assert response.status_code == 404


def test_get_transaction_nonexisting_user():
    response = client.get("users/999/transactions/1")
    assert response.status_code == 404


def test_create_transaction(deposit_transaction):
    response = client.post("users/2/transactions", json=deposit_transaction)
    assert response.status_code == 200
    transaction = response.json()
    assert transaction["user_id"] == 2
    assert transaction["amount"] == 10.5
    assert transaction["type"] == "deposit"
    assert transaction["date"] == date.today().isoformat()
    assert transaction["state"] == "pending"

def test_get_balance():
    response_1 = client.get("users/1/transactions/balance").json()
    balance_1 = response_1['balance']
    assert balance_1== 0
    future_withdrawals_1 = response_1['future_withdrawals']
    assert len(future_withdrawals_1) == 3
    response_2 = client.get("users/2/transactions/balance").json()
    balance_2 = response_2['balance']
    assert balance_2== 0
    future_withdrawals_2 = response_2['future_withdrawals']
    assert len(future_withdrawals_2) == 5
    response_3 = client.get("users/3/transactions/balance").json()
    balance_3 = response_3['balance']
    assert balance_3== 30
    future_withdrawals_3 = response_3['future_withdrawals']
    assert len(future_withdrawals_3) == 1