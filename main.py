"""
TRADING BOT - Hệ thống giao dịch tự động sử dụng ChatGPT + Binance
Phù hợp cho học sinh cấp 3

Luồng hoạt động:
1. Thu thập dữ liệu từ Binance
2. Tính chỉ báo kỹ thuật (MA, RSI, ATR)
3. ChatGPT phân tích và khuyến nghị
4. Thực thi lệnh (nếu khuyến nghị hợp lý)
5. Log và báo cáo

⚠️ CHỈ DÙNG BINANCE TESTNET - KHÔNG DÙNG TIỀN THẬT!
"""

import time
from datetime import datetime
import traceback

# Import các module đã tạo
from data_collector import DataCollector
from technical_indicators import TechnicalIndicators
from chatgpt_advisor import ChatGPTAdvisor
from trade_executor import TradeExecutor
from risk_manager import RiskOrderManager
from database_logger import DatabaseLogger
from reporting_monitoring import ReportingMonitoring
import config


class TradingBot:
    """
    Bot giao dịch tự động chính
    """
    
    def __init__(self):
        """Khởi tạo tất cả components"""
        print("🚀 Khởi tạo Trading Bot...")
        
        self.data_collector = DataCollector()
        self.indicators = TechnicalIndicators()
        self.advisor = ChatGPTAdvisor()
        self.executor = TradeExecutor()
        
        # Các module mới
        account_balance = self._get_account_balance()
        self.risk_manager = RiskOrderManager(account_balance=account_balance)
        self.database_logger = DatabaseLogger()
        self.reporting = ReportingMonitoring()
        
        self.symbol = config.TRADE_SYMBOL
        self.running = False
        
        print("✅ Bot đã sẵn sàng!\n")
    
    def _get_account_balance(self):
        """Lấy số dư tài khoản"""
        try:
            # Tạo executor tạm để lấy số dư
            temp_executor = TradeExecutor()
            balances = temp_executor.get_account_balance()
            return balances.get('USDT', 10000)  # Mặc định 10000 nếu không có
        except:
            return 10000
    
    def run_once(self):
        """
        Chạy một chu kỳ phân tích + giao dịch
        
        Returns:
            dict: Kết quả phân tích
        """
        print("=" * 60)
        print(f"📊 Chu kỳ phân tích - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        try:
            # Bước 1: Thu thập dữ liệu
            print("\n1️⃣ Thu thập dữ liệu từ Binance...")
            data = self.data_collector.get_realtime_data(
                symbol=self.symbol,
                interval='15m'  # Dùng khung 15 phút
            )
            
            if data['candles'].empty:
                print("⚠️ Không có dữ liệu!")
                return None
            
            # Bước 2: Tính chỉ báo kỹ thuật
            print("\n2️⃣ Tính toán chỉ báo kỹ thuật...")
            indicators = self.indicators.get_all_indicators(
                data['candles'],
                ma_period=config.MA_PERIOD,
                rsi_period=config.RSI_PERIOD,
                atr_period=config.ATR_PERIOD
            )
            
            print(f"   💰 Giá hiện tại: ${indicators['current_price']:.2f}")
            print(f"   📈 MA({config.MA_PERIOD}): ${indicators['ma']:.2f}")
            print(f"   📊 RSI({config.RSI_PERIOD}): {indicators['rsi']:.2f}")
            print(f"   📉 ATR({config.ATR_PERIOD}): ${indicators['atr']:.2f}")
            
            # Phân tích nhanh
            if indicators['rsi'] > 70:
                print("   ⚠️ RSI QUÁ MUA - Thị trường có thể giảm")
            elif indicators['rsi'] < 30:
                print("   ✅ RSI QUÁ BÁN - Thị trường có thể tăng")
            
            # Bước 3: ChatGPT phân tích
            print("\n3️⃣ ChatGPT đang phân tích...")
            advice = self.advisor.analyze_market(
                symbol=self.symbol,
                current_price=indicators['current_price'],
                ma=indicators['ma'],
                rsi=indicators['rsi'],
                atr=indicators['atr']
            )
            
            print(f"\n🤖 KHUYẾN NGHỊ: {advice['recommendation']}")
            print(f"💬 Lý do: {advice['reason']}")
            
            # Lưu dữ liệu phân tích vào database
            self.database_logger.save_analysis_data(indicators, advice, symbol=self.symbol)
            
            # Bước 4: Risk Manager kiểm tra điều kiện
            print("\n4️⃣ Risk Manager đang kiểm tra điều kiện...")
            
            can_execute, reason = self.risk_manager.check_risk_conditions(indicators, advice)
            
            if not can_execute:
                print(f"⏸️ KHÔNG giao dịch: {reason}")
                should_execute = False
            else:
                print(f"✅ Điều kiện OK: {reason}")
                should_execute = True
            
            # Bước 5: Thực thi lệnh nếu đủ điều kiện
            if should_execute and advice['recommendation'] in ['BUY', 'SELL']:
                print("\n5️⃣ Thực thi lệnh...")
                self._execute_trade(advice['recommendation'], indicators, advice)
            else:
                print("\n⏸️ Tạm thời GIỮ vị thế - Không giao dịch")
            
            # Lưu kết quả
            result = {
                'timestamp': datetime.now(),
                'price': indicators['current_price'],
                'ma': indicators['ma'],
                'rsi': indicators['rsi'],
                'atr': indicators['atr'],
                'recommendation': advice['recommendation'],
                'reason': advice['reason'],
                'executed': should_execute
            }
            
            self._log_result(result)
            
            return result
            
        except Exception as e:
            print(f"❌ Lỗi trong chu kỳ phân tích: {e}")
            traceback.print_exc()
            return None
    
    def _should_execute(self, indicators, advice):
        """
        Quyết định có nên thực thi lệnh không (DEPRECATED - dùng risk_manager)
        """
        # Kiểm tra lệnh mở
        open_orders = self.executor.get_open_orders(self.symbol)
        if len(open_orders) > 0:
            print("   ⚠️ Đã có lệnh mở - Không giao dịch mới")
            return False
        
        return True
    
    def _execute_trade(self, recommendation, indicators, advice):
        """
        Thực thi lệnh giao dịch với Risk Manager
        """
        try:
            # Lấy giá hiện tại
            current_price = indicators['current_price']
            current_atr = indicators['atr']
            
            # Risk Manager tính toán vị thế
            position_info = self.risk_manager.calculate_position_size(
                entry_price=current_price,
                signal=recommendation,
                current_atr=current_atr
            )
            
            if not position_info or position_info['quantity'] == 0:
                print("   ⚠️ Không đủ vốn hoặc quantity = 0")
                return
            
            quantity = position_info['quantity']
            
            # Đặt lệnh và lưu vào database
            if recommendation == 'BUY':
                order = self.executor.place_market_buy(self.symbol, quantity)
                if order:
                    self.database_logger.save_trading_record(order, position_info)
            elif recommendation == 'SELL':
                order = self.executor.place_market_sell(self.symbol, quantity)
                if order:
                    self.database_logger.save_trading_record(order, position_info)
            
        except Exception as e:
            print(f"   ❌ Lỗi thực thi: {e}")
    
    def _log_result(self, result):
        """Lưu kết quả vào file log"""
        try:
            with open(config.LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"\n{result['timestamp']} | "
                       f"Price: ${result['price']:.2f} | "
                       f"RSI: {result['rsi']:.2f} | "
                       f"Advice: {result['recommendation']} | "
                       f"Executed: {result['executed']}\n")
        except Exception as e:
            print(f"⚠️ Lỗi ghi log: {e}")
    
    def run_continuous(self, interval_minutes=15):
        """
        Chạy bot liên tục
        
        Args:
            interval_minutes: Chu kỳ phân tích (phút)
        """
        self.running = True
        print(f"\n🔄 Bắt đầu chạy bot - Chu kỳ: {interval_minutes} phút")
        print("   Nhấn Ctrl+C để dừng\n")
        
        try:
            while self.running:
                self.run_once()
                
                print(f"\n⏰ Chờ {interval_minutes} phút đến chu kỳ tiếp theo...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n\n⚠️ Bot dừng bởi người dùng")
            self.running = False


def main():
    """
    Hàm main - Entry point của bot
    """
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         TRADING BOT - ChatGPT + Binance Testnet           ║
    ║                Phù hợp cho học sinh cấp 3                  ║
    ╚═══════════════════════════════════════════════════════════╝
    
    ⚠️ CHỈ DÙNG BINANCE TESTNET - KHÔNG DÙNG TIỀN THẬT!
    """)
    
    bot = TradingBot()
    
    # Chọn chế độ chạy
    print("Chọn chế độ:")
    print("0️⃣ Chạy với GIAO DIỆN GUI (Tkinter)")
    print("1️⃣ Chạy MỘT LẦN (phân tích và dừng)")
    print("2️⃣ Chạy LIÊN TỤC (tự động mỗi 15 phút)")
    print("3️⃣ Chạy DEMO (không giao dịch)")
    print("4️⃣ Xem BÁO CÁO hiệu suất")
    
    choice = input("\n👉 Nhập lựa chọn (0/1/2/3/4): ")
    
    if choice == '0':
        # Chạy GUI mode
        try:
            import tkinter as tk
            from gui_app import TradingBotGUI
            
            root = tk.Tk()
            app = TradingBotGUI(root, bot)
            root.mainloop()
        except ImportError:
            print("❌ Không tìm thấy module tkinter hoặc gui_app!")
            print("💡 Hãy cài tkinter: pip install tk")
    
    elif choice == '1':
        bot.run_once()
    elif choice == '2':
        bot.run_continuous(interval_minutes=15)
    elif choice == '3':
        print("\n📊 DEMO MODE - Chỉ phân tích, không giao dịch")
        bot.run_once()
    elif choice == '4':
        print("\n📊 XEM BÁO CÁO...")
        bot.reporting.generate_summary_report()
        bot.reporting.plot_equity_curve()
        bot.reporting.export_html_report()
        print("\n✅ Đã xuất báo cáo: trading_report.html và equity_curve.png")
    else:
        print("❌ Lựa chọn không hợp lệ!")


if __name__ == '__main__':
    main()

