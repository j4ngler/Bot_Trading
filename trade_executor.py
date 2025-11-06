"""
Module thực thi lệnh giao dịch
CHỈ DÙNG BINANCE TESTNET - AN TOÀN cho học sinh!
"""

from binance.client import Client
import config
import sqlite3
from datetime import datetime
import time


class TradeExecutor:
    """
    Class thực thi lệnh giao dịch trên Binance Testnet
    
    CHÚ Ý:
    - CHỈ dùng Testnet (testnet=True)
    - KHÔNG dùng tiền thật
    - An toàn cho học sinh thử nghiệm
    """
    
    def __init__(self):
        """Khởi tạo kết nối Binance Testnet"""
        try:
            self.client = Client(
                api_key=config.BINANCE_API_KEY,
                api_secret=config.BINANCE_SECRET_KEY,
                testnet=True  # QUAN TRỌNG: Chỉ dùng Testnet
            )
            print("✅ Trade Executor đã sẵn sàng (Testnet)")
        except Exception as e:
            print(f"❌ Lỗi khởi tạo: {e}")
    
    def get_account_balance(self):
        """
        Kiểm tra số dư tài khoản (Testnet)
        
        Returns:
            dict: {'USDT': 10000, 'BTC': 0.0, ...}
        """
        try:
            account = self.client.get_account()
            balances = {}
            for balance in account['balances']:
                if float(balance['free']) > 0:
                    balances[balance['asset']] = float(balance['free'])
            return balances
        except Exception as e:
            print(f"❌ Lỗi kiểm tra số dư: {e}")
            return {}
    
    def calculate_quantity(self, price, risk_percent=1.0):
        """
        Tính số lượng trade dựa trên rủi ro
        
        Công thức: quantity = (vốn * risk_percent) / (price * stop_loss_percent)
        
        Args:
            price: Giá hiện tại
            risk_percent: % vốn chấp nhận rủi ro (mặc định 1%)
        
        Returns:
            float: Số lượng cần mua
        """
        balances = self.get_account_balance()
        usdt_balance = balances.get('USDT', 0)
        
        if usdt_balance == 0:
            print("⚠️ Không có USDT trong tài khoản!")
            return 0
        
        # Tính số tiền chấp nhận rủi ro
        risk_amount = usdt_balance * (risk_percent / 100)
        
        # Tính quantity với stop loss 2%
        stop_loss_amount = price * (config.STOP_LOSS_PERCENT / 100)
        quantity = risk_amount / stop_loss_amount
        
        print(f"💰 Số dư: ${usdt_balance:.2f} USDT")
        print(f"⚠️ Rủi ro: ${risk_amount:.2f} ({risk_percent}%)")
        print(f"📊 Số lượng: {quantity:.6f}")
        
        return quantity
    
    def place_market_buy(self, symbol, quantity):
        """
        Đặt lệnh MUA (Market Buy)
        
        Args:
            symbol: Mã giao dịch (vd: BTCUSDT)
            quantity: Số lượng
        
        Returns:
            dict: Thông tin lệnh đã đặt
        """
        try:
            print(f"📈 Đang mua {quantity} {symbol}...")
            
            order = self.client.create_order(
                symbol=symbol,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity
            )
            
            print(f"✅ Lệnh MUA thành công!")
            print(f"   Order ID: {order['orderId']}")
            
            # Lưu vào database
            self._save_order(order, 'BUY')
            
            return order
            
        except Exception as e:
            print(f"❌ Lỗi đặt lệnh MUA: {e}")
            return None
    
    def place_market_sell(self, symbol, quantity):
        """
        Đặt lệnh BÁN (Market Sell)
        
        Args:
            symbol: Mã giao dịch
            quantity: Số lượng
        
        Returns:
            dict: Thông tin lệnh đã đặt
        """
        try:
            print(f"📉 Đang bán {quantity} {symbol}...")
            
            order = self.client.create_order(
                symbol=symbol,
                side=Client.SIDE_SELL,
                type=Client.ORDER_TYPE_MARKET,
                quantity=quantity
            )
            
            print(f"✅ Lệnh BÁN thành công!")
            print(f"   Order ID: {order['orderId']}")
            
            # Lưu vào database
            self._save_order(order, 'SELL')
            
            return order
            
        except Exception as e:
            print(f"❌ Lỗi đặt lệnh BÁN: {e}")
            return None
    
    def _save_order(self, order, action):
        """
        Lưu lịch sử lệnh vào database
        
        Args:
            order: Thông tin lệnh từ Binance
            action: 'BUY' hoặc 'SELL'
        """
        try:
            conn = sqlite3.connect(config.DATABASE_FILE)
            cursor = conn.cursor()
            
            # Tạo bảng nếu chưa có
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id TEXT,
                    symbol TEXT,
                    side TEXT,
                    quantity REAL,
                    price REAL,
                    status TEXT,
                    timestamp TEXT
                )
            ''')
            
            # Thêm dữ liệu
            cursor.execute('''
                INSERT INTO orders (order_id, symbol, side, quantity, price, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                order['orderId'],
                order['symbol'],
                action,
                order['executedQty'],
                order.get('price', 0),
                order['status'],
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Lỗi lưu database: {e}")
    
    def get_open_orders(self, symbol):
        """
        Lấy danh sách lệnh đang mở
        
        Returns:
            list: Danh sách lệnh
        """
        try:
            orders = self.client.get_open_orders(symbol=symbol)
            return orders
        except Exception as e:
            print(f"❌ Lỗi lấy lệnh mở: {e}")
            return []


if __name__ == '__main__':
    # Test module
    print("🧪 Testing Trade Executor...")
    
    executor = TradeExecutor()
    
    # Kiểm tra số dư
    print("\n💰 Số dư tài khoản:")
    balance = executor.get_account_balance()
    for asset, amount in balance.items():
        print(f"   {asset}: {amount}")
    
    # Tính số lượng trade
    print("\n📊 Tính toán rủi ro:")
    quantity = executor.calculate_quantity(price=43250.0, risk_percent=1.0)
    print(f"   Số lượng: {quantity} BTC")

