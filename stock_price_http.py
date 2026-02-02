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
def get_stock_price(symbol: str):
    if not symbol:
        raise HTTPException(status_code=400, detail="請提供股票代號")
    try:
        ticker = yf.Ticker(symbol)
        # 獲取最近兩天的數據以計算漲跌
        hist = ticker.history(period="2d")
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"找不到 {symbol} 的股價資訊")

        # 獲取最新收盤價
        price = float(hist['Close'].iloc[-1])

        # 計算漲跌
        if len(hist) > 1:
            prev_close = float(hist['Close'].iloc[-2])
            change = price - prev_close
            percent_change = (change / prev_close) * 100
        else:
            change = 0.0
            percent_change = 0.0

        return {
            "symbol": symbol.upper(),
            "price": price,
            "change": round(change, 2),
            "percent_change": round(percent_change, 2)
        }
    except HTTPException:
        # 重新拋出 HTTPException 避免被下方的 Exception 捕獲
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢 {symbol} 時發生錯誤: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
