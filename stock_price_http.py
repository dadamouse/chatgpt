import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import yfinance as yf
import os

app = FastAPI()

# 建立 static 資料夾（如果不存在）
if not os.path.exists("static"):
    os.makedirs("static")

# 掛載 static 資料夾
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.get("/api")
async def get_stock_price(symbol: str):
    if not symbol:
        raise HTTPException(status_code=400, detail="請提供股票代號")
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"找不到 {symbol} 的股價資料")
        price = hist['Close'].iloc[-1]
        return {"symbol": symbol, "price": round(price, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢 {symbol} 時發生錯誤: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
