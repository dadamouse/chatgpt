import uvicorn  sdfsdfsdfs
from fastapi import FastAPI, Request
from typing import Dict, Any
import yfinance as yf

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
                "description": "查詢指定股票的即時股價（使用 Yahoo Finance via yfinance）",
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

        try:
            ticker = yf.Ticker(symbol)
            price = ticker.info.get("regularMarketPrice")
            if price is None:
                return {"content": [{"type": "text", "text": f"找不到 {symbol} 的即時股價"}]}
            
            return {"content": [{"type": "text", "text": f"{symbol} 當前股價: {price}"}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"查詢 {symbol} 時發生錯誤: {str(e)}"}]}

    return {"content": [{"type": "text", "text": f"未知工具: {tool}"}]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
