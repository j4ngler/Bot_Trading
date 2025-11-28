"""
Module thu thập dữ liệu từ Binance Testnet
Phù hợp cho học sinh cấp 3 - có comment giải thích chi tiết
"""

import pandas as pd
import sqlite3
import time
from datetime import datetime
from binance.client import Client
from . import config


class DataCollector:
    """
    Class thu thập dữ liệu giá từ Binance
    - Lấy giá real-time
    - Lấy dữ liệu candle (nến) qua các khung thời gian
    - Lưu vào SQLite database
    """
    
    def __init__(self):
        """Khởi tạo kết nối với Binance Testnet"""
        try:
            # Binance Testnet - AN TOÀN, không dùng tiền thật!
            self.client = Client(
                api_key=config.BINANCE_API_KEY,
                api_secret=config.BINANCE_SECRET_KEY,
                testnet=True  # QUAN TRỌNG: dùng Testnet
            )
            print("✅ Kết nối thành công với Binance Testnet")
        except Exception as e:
            print(f"❌ Lỗi kết nối Binance: {e}")
            print("💡 Hướng dẫn:")
            print("   1. Truy cập: https://testnet.binance.vision/")
            print("   2. Đăng ký/đăng nhập")
            print("   3. Tạo API Key và Secret")
            print("   4. Điền vào file .env")
    
    def get_current_price(self, symbol='BTCUSDT'):
        """
        Lấy giá hiện tại của một symbol
        
        Args:
            symbol: Mã giao dịch (vd: BTCUSDT, ETHUSDT)
        
        Returns:
            float: Giá hiện tại
        """
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            return price
        except Exception as e:
            print(f"❌ Lỗi lấy giá {symbol}: {e}")
            return None
    
    def get_candles(self, symbol='BTCUSDT', interval='1m', limit=100):
        """
        Lấy dữ liệu candle (nến) từ Binance
        
        Args:
            symbol: Mã giao dịch
            interval: Khung thời gian (1m, 5m, 15m, 1h, 1d...)
            limit: Số lượng candle muốn lấy (tối đa 1000)
        
        Returns:
            DataFrame: Dữ liệu với các cột:
                - open_time: Thời gian mở
                - open: Giá mở
                - high: Giá cao nhất
                - low: Giá thấp nhất
                - close: Giá đóng
                - volume: Khối lượng giao dịch
        """
        try:
            # Lấy dữ liệu từ Binance
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            # Chuyển thành DataFrame để dễ xử lý
            df = pd.DataFrame(klines, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            
            # Chuyển sang kiểu số thực
            df['open'] = pd.to_numeric(df['open'])
            df['high'] = pd.to_numeric(df['high'])
            df['low'] = pd.to_numeric(df['low'])
            df['close'] = pd.to_numeric(df['close'])
            df['volume'] = pd.to_numeric(df['volume'])
            
            # Chuyển open_time thành datetime
            df['datetime'] = pd.to_datetime(df['open_time'], unit='ms')
            
            print(f"✅ Lấy được {len(df)} candle {interval} cho {symbol}")
            return df
            
        except Exception as e:
            print(f"❌ Lỗi lấy candle: {e}")
            return pd.DataFrame()  # Trả về DataFrame rỗng
    
    def get_realtime_data(self, symbol='BTCUSDT', interval='1m'):
        """
        Hàm tiện ích: Lấy dữ liệu real-time mới nhất
        
        Returns:
            dict: {
                'price': giá hiện tại,
                'candles': DataFrame candles,
                'timestamp': thời gian lấy
            }
        """
        data = {
            'timestamp': datetime.now(),
            'price': self.get_current_price(symbol),
            'candles': self.get_candles(symbol, interval, limit=100)
        }
        return data


if __name__ == '__main__':
    # Test module
    print("🧪 Testing Data Collector...")
    
    collector = DataCollector()
    
    # Lấy giá hiện tại
    price = collector.get_current_price()
    print(f"\n💰 Giá BTC/USDT hiện tại: ${price}")
    
    # Lấy candles
    candles = collector.get_candles(limit=10)
    print("\n📊 10 candle gần nhất:")
    print(candles[['datetime', 'open', 'high', 'low', 'close', 'volume']].tail())

