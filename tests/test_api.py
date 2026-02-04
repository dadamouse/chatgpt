from fastapi.testclient import TestClient
from stock_price_http import app

client = TestClient(app)

def test_read_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "即時股價查詢" in response.text

def test_get_stock_price_success():
    # Use a well-known symbol
    response = client.get("/api?symbol=2330.TW")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "2330.TW"
    assert "price" in data
    assert "change" in data
    assert "percent_change" in data
    assert "open" in data
    assert "high" in data
    assert "low" in data
    assert "volume" in data

def test_get_stock_price_no_symbol():
    response = client.get("/api?symbol=")
    assert response.status_code == 400

def test_get_stock_price_invalid_symbol():
    response = client.get("/api?symbol=INVALID_SYMBOL_12345")
    assert response.status_code == 404
