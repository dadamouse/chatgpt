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
        info = ticker.info

        # yfinance might return an empty info dict if the symbol is not found
        if not info or info.get('regularMarketPrice') is None:
            # For some symbols (like indices), 'regularMarketPrice' might not be available.
            # Let's try another key to be sure.
            history = ticker.history(period="1d")
            if history.empty:
                 raise HTTPException(status_code=404, detail=f"找不到股票代號 {symbol} 的相關資訊")
            # If history is available, extract info from there
            latest = history.iloc[-1]
            price = latest['Close']
            day_high = latest['High']
            day_low = latest['Low']
            volume = latest['Volume']
            short_name = symbol # Fallback to symbol if shortName not in info
        else:
            price = info.get("regularMarketPrice")
            short_name = info.get("shortName")
            day_high = info.get("dayHigh")
            day_low = info.get("dayLow")
            volume = info.get("volume")


        return {
            "symbol": symbol,
            "price": price,
            "shortName": short_name,
            "dayHigh": day_high,
            "dayLow": day_low,
            "volume": volume
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢 {symbol} 時發生錯誤: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
