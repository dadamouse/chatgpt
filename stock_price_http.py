import uvicorn
from fastapi import FastAPI, Request
from typing import Dict, Any
import yfinance as yf
import pandas as pd
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    filename='stock_queries.log',
                    filemode='a')
logger = logging.getLogger(__name__)

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
                "description": "查詢指定股票的即時股價與移動平均線 (MA) 數據（使用 Yahoo Finance via yfinance）",
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
            # 下載最近 4 個月的歷史數據以確保有足夠的資料計算 MA60
            data = yf.download(symbol, period="4mo", progress=False)
            if data.empty:
                return {"content": [{"type": "text", "text": f"找不到 {symbol} 的歷史股價數據"}]}

            # 取得最新價格
            price = data['Close'].iloc[-1]

            # 計算移動平均線
            ma5 = data['Close'].rolling(window=5).mean().iloc[-1]
            ma20 = data['Close'].rolling(window=20).mean().iloc[-1]
            ma60 = data['Close'].rolling(window=60).mean().iloc[-1]

            # 格式化輸出訊息
            response_text = (
                f"{symbol} 當前股價: {float(price):.2f}\n"
                f"MA5: {float(ma5):.2f}\n"
                f"MA20: {float(ma20):.2f}\n"
                f"MA60: {float(ma60):.2f}"
            )
            
            # 記錄查詢結果
            logger.info(f"Symbol: {symbol}, Price: {float(price):.2f}, MA5: {float(ma5):.2f}, MA20: {float(ma20):.2f}, MA60: {float(ma60):.2f}")

            return {"content": [{"type": "text", "text": response_text}]}
        except Exception as e:
            logger.error(f"Error querying {symbol}: {str(e)}")
            return {"content": [{"type": "text", "text": f"查詢 {symbol} 時發生錯誤: {str(e)}"}]}

    return {"content": [{"type": "text", "text": f"未知工具: {tool}"}]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
