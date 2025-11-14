"""
Module Database & Logger
- Lưu lịch sử giao dịch
- Lưu dữ liệu phân tích
- Lưu kết quả và báo cáo
- Cung cấp phản hồi hiệu quả cho AI
"""

import sqlite3
import json
from datetime import datetime
import os
from . import config


class DatabaseLogger:
    """
    Class quản lý database và logging
    
    Chức năng:
    1. Lưu dữ liệu phân tích (indicators, ChatGPT advice)
    2. Lưu lịch sử giao dịch
    3. Lưu kết quả và performance
    4. Tạo báo cáo và phản hồi cho AI
    """
    
    def __init__(self, db_file=None):
        """
        Khởi tạo Database Logger
        
        Args:
            db_file: Đường dẫn file database (mặc định từ config)
        """
        self.db_file = db_file or config.DATABASE_FILE
        # Đảm bảo thư mục data tồn tại
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        self._init_database()
        print("✅ Database & Logger đã sẵn sàng")
    
    def _init_database(self):
        """Khởi tạo các bảng trong database"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Bảng lưu dữ liệu phân tích
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    symbol TEXT,
                    price REAL,
                    ma REAL,
                    rsi REAL,
                    atr REAL,
                    recommendation TEXT,
                    reason TEXT,
                    confidence REAL,
                    raw_response TEXT
                )
            ''')
            
            # Bảng lưu lịch sử giao dịch
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trading_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    order_id TEXT,
                    symbol TEXT,
                    side TEXT,
                    quantity REAL,
                    entry_price REAL,
                    exit_price REAL,
                    stop_loss REAL,
                    take_profit REAL,
                    status TEXT,
                    pnl REAL,
                    pnl_percent REAL
                )
            ''')
            
            # Bảng lưu kết quả performance
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_trades INTEGER,
                    winning_trades INTEGER,
                    losing_trades INTEGER,
                    total_pnl REAL,
                    win_rate REAL,
                    avg_win REAL,
                    avg_loss REAL,
                    profit_factor REAL,
                    account_balance REAL
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Lỗi khởi tạo database: {e}")
    
    def save_analysis_data(self, indicators, advice, symbol='BTCUSDT'):
        """
        Lưu dữ liệu phân tích (từ bộ tính toán chỉ báo và ChatGPT)
        
        Args:
            indicators: dict từ technical_indicators
            advice: dict từ chatgpt_advisor
            symbol: Mã giao dịch
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO analysis_data 
                (timestamp, symbol, price, ma, rsi, atr, recommendation, reason, confidence, raw_response)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                symbol,
                indicators.get('current_price'),
                indicators.get('ma'),
                indicators.get('rsi'),
                indicators.get('atr'),
                advice.get('recommendation'),
                advice.get('reason'),
                advice.get('confidence'),
                advice.get('raw_response', '')
            ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Đã lưu dữ liệu phân tích: {advice.get('recommendation')}")
            
        except Exception as e:
            print(f"❌ Lỗi lưu phân tích: {e}")
    
    def save_trading_record(self, order_info, position_info=None):
        """
        Lưu lịch sử giao dịch
        
        Args:
            order_info: Thông tin lệnh từ Binance
            position_info: Thông tin về vị thế (stop loss, take profit)
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            # Lấy thông tin từ order_info
            order_id = order_info.get('orderId', '')
            symbol = order_info.get('symbol', '')
            side = 'BUY' if order_info.get('side') == 'BUY' else 'SELL'
            quantity = float(order_info.get('executedQty', 0))
            
            # Tính giá entry: ưu tiên từ position_info, sau đó từ order response
            if position_info and position_info.get('entry_price'):
                price = float(position_info['entry_price'])
            elif order_info.get('cummulativeQuoteQty') and quantity > 0:
                # Market order: tính giá từ cummulativeQuoteQty / executedQty
                price = float(order_info.get('cummulativeQuoteQty', 0)) / quantity
            elif order_info.get('price'):
                price = float(order_info.get('price', 0))
            else:
                # Fallback: lấy giá hiện tại từ ticker
                try:
                    from .trade_executor import TradeExecutor
                    temp_executor = TradeExecutor()
                    ticker = temp_executor.client.get_symbol_ticker(symbol=symbol)
                    price = float(ticker['price']) if ticker else 0.0
                except:
                    price = 0.0
            
            # Lấy thông tin từ position_info nếu có
            stop_loss = position_info.get('stop_loss', 0) if position_info else 0
            take_profit = position_info.get('take_profit', 0) if position_info else 0
            
            cursor.execute('''
                INSERT INTO trading_history 
                (timestamp, order_id, symbol, side, quantity, entry_price, stop_loss, take_profit, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                str(order_id),
                symbol,
                side,
                quantity,
                price,
                stop_loss,
                take_profit,
                order_info.get('status', 'FILLED')
            ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Đã lưu lệnh giao dịch: {side} {quantity} {symbol}")
            
        except Exception as e:
            print(f"❌ Lỗi lưu lệnh: {e}")
    
    def save_performance_report(self, total_trades, winning_trades, losing_trades,
                                total_pnl, account_balance):
        """
        Lưu báo cáo hiệu suất
        
        Args:
            total_trades: Tổng số lệnh
            winning_trades: Số lệnh thắng
            losing_trades: Số lệnh thua
            total_pnl: Tổng PnL
            account_balance: Số dư tài khoản hiện tại
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            # Tính các chỉ số
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            cursor.execute('''
                INSERT INTO performance 
                (timestamp, total_trades, winning_trades, losing_trades, 
                 total_pnl, win_rate, account_balance)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                total_trades,
                winning_trades,
                losing_trades,
                total_pnl,
                win_rate,
                account_balance
            ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Đã lưu báo cáo hiệu suất: Win Rate = {win_rate:.2f}%")
            
        except Exception as e:
            print(f"❌ Lỗi lưu performance: {e}")
    
    def get_performance_feedback(self):
        """
        Lấy phản hồi hiệu quả giao dịch để gửi lại cho ChatGPT
        
        Returns:
            dict: Thông tin performance gần đây
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Lấy báo cáo mới nhất
            cursor.execute('''
                SELECT * FROM performance 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''')
            
            latest = cursor.fetchone()
            
            # Đếm lệnh gần đây (7 ngày)
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'FILLED' THEN 1 ELSE 0 END) as filled
                FROM trading_history
                WHERE timestamp >= datetime('now', '-7 days')
            ''')
            
            recent_stats = cursor.fetchone()
            
            conn.close()
            
            if latest:
                feedback = {
                    'total_trades': latest[2],
                    'win_rate': latest[6],
                    'total_pnl': latest[5],
                    'account_balance': latest[10],
                    'recent_activity': recent_stats[0] if recent_stats else 0
                }
            else:
                feedback = {
                    'total_trades': 0,
                    'win_rate': 0,
                    'total_pnl': 0,
                    'account_balance': 0,
                    'recent_activity': 0
                }
            
            return feedback
            
        except Exception as e:
            print(f"❌ Lỗi lấy feedback: {e}")
            return {}
    
    def get_trading_statistics(self, days=30):
        """
        Lấy thống kê giao dịch
        
        Args:
            days: Số ngày cần xem
        
        Returns:
            dict: Thống kê giao dịch
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Đếm tổng lệnh
            cursor.execute('''
                SELECT COUNT(*) FROM trading_history
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            total_trades = cursor.fetchone()[0]
            
            # Đếm lệnh thắng/thua (giả định status='FILLED' là thành công)
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losses,
                    AVG(pnl) as avg_pnl
                FROM trading_history
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                AND pnl IS NOT NULL
            ''', (days,))
            
            stats = cursor.fetchone()
            
            conn.close()
            
            return {
                'total_trades': total_trades,
                'wins': stats[1] if stats and stats[1] else 0,
                'losses': stats[2] if stats and stats[2] else 0,
                'avg_pnl': stats[3] if stats and stats[3] else 0
            }
            
        except Exception as e:
            print(f"❌ Lỗi lấy thống kê: {e}")
            return {}
    
    def export_to_json(self, output_file='trading_data.json'):
        """Xuất dữ liệu ra file JSON"""
        try:
            conn = sqlite3.connect(self.db_file)
            
            # Lấy tất cả analysis data
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM analysis_data')
            analysis_data = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute('SELECT * FROM trading_history')
            trading_history = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute('SELECT * FROM performance')
            performance = [dict(row) for row in cursor.fetchall()]
            
            data = {
                'analysis_data': analysis_data,
                'trading_history': trading_history,
                'performance': performance,
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            conn.close()
            
            print(f"✅ Đã xuất dữ liệu ra {output_file}")
            
        except Exception as e:
            print(f"❌ Lỗi xuất JSON: {e}")


if __name__ == '__main__':
    # Test module
    print("🧪 Testing Database & Logger...")
    
    logger = DatabaseLogger()
    
    # Test lưu dữ liệu phân tích
    print("\n📊 Test lưu dữ liệu phân tích:")
    indicators = {
        'current_price': 43250.0,
        'ma': 42800.0,
        'rsi': 65.5,
        'atr': 250.0
    }
    
    advice = {
        'recommendation': 'BUY',
        'reason': 'RSI tốt, xu hướng tăng',
        'confidence': 75
    }
    
    logger.save_analysis_data(indicators, advice)
    
    # Test lấy feedback
    print("\n📈 Test lấy performance feedback:")
    feedback = logger.get_performance_feedback()
    print(f"Feedback: {feedback}")
    
    # Test xuất JSON
    print("\n💾 Test xuất dữ liệu ra JSON:")
    logger.export_to_json()

