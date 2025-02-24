import pytest
from fastapi import status

# Test for Creating a New Order
def test_create_order(test_client):
    response = test_client.post(
        "/orders/",
        json={
            "symbol": "AAPL",
            "price": 150.5,
            "quantity": 10,
            "order_type": "buy"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["price"] == 150.5
    assert data["quantity"] == 10
    assert data["order_type"] == "buy"
    assert data["status"] == "pending"

# Test for Fetching All Orders
def test_get_orders(test_client):
    # Create an order first to ensure there's at least one order to fetch
    test_client.post(
        "/orders/",
        json={
            "symbol": "GOOGL",
            "price": 2800.0,
            "quantity": 2,
            "order_type": "buy"
        }
    )

    # Fetch all orders
    response = test_client.get("/orders/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0  # Ensure at least one order is present
    assert any(order["symbol"] == "GOOGL" for order in data)

# Test for Updating an Order Status
def test_update_order(test_client):
    # Create an order first
    create_response = test_client.post(
        "/orders/",
        json={
            "symbol": "TSLA",
            "price": 700.0,
            "quantity": 5,
            "order_type": "sell"
        }
    )
    assert create_response.status_code == status.HTTP_200_OK
    order_id = create_response.json()["id"]

    # Update the order status
    update_response = test_client.put(f"/orders/{order_id}?status=completed")
    assert update_response.status_code == status.HTTP_200_OK
    data = update_response.json()
    assert data["status"] == "completed"

    # Verify the update
    get_response = test_client.get("/orders/")
    orders = get_response.json()
    updated_order = next(order for order in orders if order["id"] == order_id)
    assert updated_order["status"] == "completed"
