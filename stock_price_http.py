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
        # 獲取最近兩天的資料以計算漲跌
        hist = ticker.history(period="2d")
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"找不到 {symbol} 的股價資訊")

        # 取得最新價格及相關資訊
        latest_data = hist.iloc[-1]
        price = float(latest_data['Close'])
        open_price = float(latest_data['Open'])
        high_price = float(latest_data['High'])
        low_price = float(latest_data['Low'])
        volume = int(latest_data['Volume'])

        # 計算漲跌
        if len(hist) > 1:
            prev_price = float(hist['Close'].iloc[-2])
            change = price - prev_price
            percent_change = (change / prev_price) * 100
        else:
            change = 0.0
            percent_change = 0.0

        return {
            "symbol": symbol,
            "price": round(price, 2),
            "change": round(change, 2),
            "percent_change": round(percent_change, 2),
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "volume": volume
        }
    except HTTPException as e:
        # 重新拋出 HTTPException 以避免被後面的 Exception 捕捉並轉為 500
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查詢 {symbol} 時發生錯誤: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
