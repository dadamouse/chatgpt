import uvicorn
from fastapi import FastAPI, Request
from typing import Dict, Any
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/.well-known/ai-plugin.json")
async def manifest():
    # MCP 工具清單
    return {
        "schema_version": "v1",
        "name": "StockPriceMCP",
        "tools": [
            {
                "name": "get_stock_price",
                "description": "查詢指定股票的即時股價（使用 Yahoo Finance）",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "股票代號，例如 AAPL, TSLA, 2330.TW"
                        }
                    },
                    "required": ["symbol"]
                }
            }
        ]
    }

@app.post("/call")
async def call_tool(req: Request):
    body: Dict[str, Any] = await req.json()
    tool = body.get("name")
    args = body.get("arguments", {})

    if tool == "get_stock_price":
        symbol = args["symbol"]
        url = f"https://finance.yahoo.com/quote/{symbol}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36"
        }
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return {"content": [{"type": "text", "text": f"無法存取 {url}，狀態碼: {r.status_code}"}]}

        soup = BeautifulSoup(r.text, "html.parser")
        price_tag = soup.find("fin-streamer", {"data-field": "regularMarketPrice"})

        if not price_tag:
            return {"content": [{"type": "text", "text": f"找不到 {symbol} 的股價"}]}

        price = price_tag.text.strip()
        return {"content": [{"type": "text", "text": f"{symbol} 當前股價: {price}"}]}

    return {"content": [{"type": "text", "text": f"未知工具: {tool}"}]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
