"""
Module thực thi lệnh giao dịch
CHỈ DÙNG BINANCE TESTNET - AN TOÀN cho học sinh!
"""

from binance.client import Client
from . import config
import sqlite3
from datetime import datetime
import time
from math import floor


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
    
    # ==== SYMBOL FILTER HELPERS ====
    def _get_symbol_filters(self, symbol):
        """Lấy filter của symbol (LOT_SIZE, MIN_NOTIONAL, PRICE_FILTER)."""
        info = self.client.get_symbol_info(symbol)
        if not info or 'filters' not in info:
            return {}
        filters = {f['filterType']: f for f in info['filters']}
        return filters

    def _round_step(self, value, step):
        """Làm tròn value xuống theo bước step (tránh vượt filter)."""
        step = float(step)
        if step <= 0:
            return value
        precision = int(max(0, -round(__import__('math').log10(step)))) if step < 1 else 0
        # dùng floor để không vượt quá
        return float(f"{floor(value / step) * step:.{precision}f}")

    def _adjust_quantity_for_filters(self, symbol, quantity, price):
        """Điều chỉnh quantity theo LOT_SIZE và kiểm tra MIN_NOTIONAL.

        Returns:
            tuple (qty_ok: float, reason: str|None)
        """
        try:
            f = self._get_symbol_filters(symbol)
            lot = f.get('LOT_SIZE', {})
            min_notional = f.get('MIN_NOTIONAL', {})

            step_size = lot.get('stepSize', '0.00000001')
            min_qty = float(lot.get('minQty', '0.0')) if lot else 0.0
            max_qty = float(lot.get('maxQty', '1e30')) if lot else 1e30

            # Làm tròn theo stepSize và giới hạn trong [minQty, maxQty]
            adj_qty = self._round_step(float(quantity), step_size)
            if adj_qty < min_qty:
                return 0.0, f"Khối lượng sau điều chỉnh ({adj_qty}) < minQty ({min_qty})"
            if adj_qty > max_qty:
                adj_qty = max_qty

            # Kiểm tra minNotional (giá trị lệnh tối thiểu)
            notional = adj_qty * float(price)
            min_notional_val = float(min_notional.get('minNotional', '0')) if min_notional else 0.0
            if notional < min_notional_val:
                return 0.0, f"Giá trị lệnh ({notional:.2f}) < minNotional ({min_notional_val})"

            return adj_qty, None
        except Exception as e:
            return 0.0, f"Lỗi điều chỉnh LOT_SIZE: {e}"

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
            # Lấy giá hiện tại (dùng ticker price) để kiểm tra minNotional
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            last_price = float(ticker['price']) if ticker and 'price' in ticker else 0.0

            adj_qty, reason = self._adjust_quantity_for_filters(symbol, quantity, last_price)
            if adj_qty <= 0:
                print(f"⏸️ Bỏ qua lệnh MUA: {reason}")
                return None

            print(f"📈 Đang mua {adj_qty} {symbol}...")

            order = self.client.create_order(
                symbol=symbol,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quantity=adj_qty
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
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            last_price = float(ticker['price']) if ticker and 'price' in ticker else 0.0

            adj_qty, reason = self._adjust_quantity_for_filters(symbol, quantity, last_price)
            if adj_qty <= 0:
                print(f"⏸️ Bỏ qua lệnh BÁN: {reason}")
                return None

            print(f"📉 Đang bán {adj_qty} {symbol}...")

            order = self.client.create_order(
                symbol=symbol,
                side=Client.SIDE_SELL,
                type=Client.ORDER_TYPE_MARKET,
                quantity=adj_qty
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

