from fastapi.testclient import TestClient
from stock_price_http import app
import pytest

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_get_stock_price_success():
    # 使用台積電作為測試，通常會有資料
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

def test_get_stock_price_invalid_symbol():
    response = client.get("/api?symbol=INVALID_SYMBOL")
    assert response.status_code == 404

def test_get_stock_price_no_symbol():
    response = client.get("/api")
    # FastAPI 會因為缺少 query parameter 而返回 422 Unprocessable Entity
    # 或者如果後端有自定義檢查則返回 400
    # 根據目前的代碼：
    # if not symbol: raise HTTPException(status_code=400, detail="請提供股票代號")
    # 但 symbol: str 是必填項，如果沒傳，FastAPI 會先擋下
    assert response.status_code in [400, 422]
