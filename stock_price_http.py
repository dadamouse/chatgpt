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

        # 獲取歷史數據和公司資訊
        hist = ticker.history(period="1d")
        info = ticker.info

        if hist.empty:
            raise HTTPException(status_code=404, detail=f"找不到 {symbol} 的股價數據")

        # 提取所需資訊
        latest_price = hist['Close'].iloc[-1]
        company_name = info.get('longName', 'N/A')
        day_high = hist['High'].iloc[-1]
        day_low = hist['Low'].iloc[-1]
        previous_close = info.get('previousClose', 'N/A')

        return {
            "symbol": symbol,
            "company_name": company_name,
            "price": f"{latest_price:.2f}",
            "day_high": f"{day_high:.2f}",
            "day_low": f"{day_low:.2f}",
            "previous_close": f"{previous_close:.2f}" if isinstance(previous_close, (int, float)) else "N/A"
        }
    except Exception as e:
        # 捕捉 yfinance 可能拋出的錯誤或其他例外
        if "No data found for symbol" in str(e):
             raise HTTPException(status_code=404, detail=f"找不到股票代號 {symbol} 的數據")
        raise HTTPException(status_code=500, detail=f"查詢 {symbol} 時發生錯誤: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
