import pytest
from http import HTTPStatus

@pytest.mark.parametrize("payload, expected_message", [
    ({}, "Description is required"),
    ({"description": "Test"}, "Amount is required"),
    ({"description": "Test", "amount": 100}, "Transaction type is required"),
    ({"description": "Test", "amount": 100, "transaction_type": "expense"}, "Category ID is required"),
    ({"description": "Test", "amount": "abc", "transaction_type": "expense", "category_id": 1}, "Amount must be a valid number"),
    ({"description": "Test", "amount": -100, "transaction_type": "expense", "category_id": 1}, "Amount must be a positive number"),
    ({"description": "Test", "amount": 100, "transaction_type": "invalid", "category_id": 1}, "Invalid transaction type. Must be 'income' or 'expense'"),
    ({"description": "Test", "amount": 100, "transaction_type": "expense", "category_id": 1, "date": "invalid-date"}, "Invalid date format. Use YYYY-MM-DD"),
])
def test_add_transaction_invalid_data(auth_client, payload, expected_message):
    client, user = auth_client
    response = client.post('/api/transactions', json=payload)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json['message'] == expected_message
