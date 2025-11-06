"""
Module GUI cho Trading Bot
Tích hợp vào main.py
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from datetime import datetime
import traceback


class TradingBotGUI:
    """
    Giao diện GUI cho Trading Bot
    """
    
    def __init__(self, root, trading_bot):
        self.root = root
        self.bot = trading_bot
        self.running = False
        self.is_demo = False
        self.cycle_count = 0
        
        self.setup_gui()
        self.update_info()
    
    def setup_gui(self):
        """Thiết lập giao diện"""
        self.root.title("🤖 Trading Bot - ChatGPT + Binance Testnet")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        
        # Header
        header_frame = tk.Frame(self.root, bg='#2d2d2d', height=60)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = tk.Label(header_frame, 
                              text="🚀 Trading Bot - ChatGPT + Binance Testnet",
                              font=('Arial', 16, 'bold'),
                              bg='#2d2d2d', fg='#00ff00')
        title_label.pack(pady=15)
        
        # Main Container
        main_container = tk.Frame(self.root, bg='#1e1e1e')
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left Panel - Info & Control
        left_panel = tk.Frame(main_container, bg='#2d2d2d', width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        # Right Panel - Logs & Data
        right_panel = tk.Frame(main_container, bg='#2d2d2d')
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.setup_left_panel(left_panel)
        self.setup_right_panel(right_panel)
    
    def setup_left_panel(self, parent):
        """Thiết lập panel trái - Thông tin & Điều khiển"""
        
        # Market Info Frame
        info_frame = tk.LabelFrame(parent, text="📊 Thông tin Thị trường", 
                                   bg='#2d2d2d', fg='white', font=('Arial', 10, 'bold'))
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.price_label = tk.Label(info_frame, text="Giá: $0.00", 
                                   bg='#2d2d2d', fg='#00ff00', font=('Arial', 12, 'bold'))
        self.price_label.pack(pady=5)
        
        self.ma_label = tk.Label(info_frame, text="MA(20): $0.00", 
                                bg='#2d2d2d', fg='#ffffff')
        self.ma_label.pack(anchor='w', padx=10)
        
        self.rsi_label = tk.Label(info_frame, text="RSI(14): 0.00", 
                                 bg='#2d2d2d', fg='#ffffff')
        self.rsi_label.pack(anchor='w', padx=10)
        
        self.atr_label = tk.Label(info_frame, text="ATR(14): $0.00", 
                                 bg='#2d2d2d', fg='#ffffff')
        self.atr_label.pack(anchor='w', padx=10)
        
        self.recommendation_label = tk.Label(info_frame, text="Khuyến nghị: -", 
                                           bg='#2d2d2d', fg='#ffff00', font=('Arial', 10, 'bold'))
        self.recommendation_label.pack(pady=5)
        
        # Control Frame
        control_frame = tk.LabelFrame(parent, text="🎮 Điều khiển", 
                                      bg='#2d2d2d', fg='white', font=('Arial', 10, 'bold'))
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_btn = tk.Button(control_frame, text="▶️ BẮT ĐẦU", 
                                  command=self.start_bot,
                                  bg='#4CAF50', fg='white', font=('Arial', 11, 'bold'),
                                  width=20, height=2)
        self.start_btn.pack(pady=5)
        
        self.stop_btn = tk.Button(control_frame, text="⏸️ DỪNG", 
                                 command=self.stop_bot,
                                 bg='#f44336', fg='white', font=('Arial', 11, 'bold'),
                                 width=20, height=2, state='disabled')
        self.stop_btn.pack(pady=5)
        
        self.demo_btn = tk.Button(control_frame, text="🔍 CHẠY DEMO", 
                                 command=self.run_demo,
                                 bg='#2196F3', fg='white', font=('Arial', 11, 'bold'),
                                 width=20, height=2)
        self.demo_btn.pack(pady=5)
        
        # Status Frame
        status_frame = tk.LabelFrame(parent, text="📈 Trạng thái", 
                                     bg='#2d2d2d', fg='white', font=('Arial', 10, 'bold'))
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.status_label = tk.Label(status_frame, text="🟢 Sẵn sàng", 
                                    bg='#2d2d2d', fg='#4CAF50', font=('Arial', 11))
        self.status_label.pack(pady=10)
        
        self.cycle_label = tk.Label(status_frame, text="Chu kỳ: 0", 
                                   bg='#2d2d2d', fg='#ffffff')
        self.cycle_label.pack()
        
        self.last_update_label = tk.Label(status_frame, text="Cập nhật: --", 
                                          bg='#2d2d2d', fg='#aaaaaa')
        self.last_update_label.pack()
    
    def setup_right_panel(self, parent):
        """Thiết lập panel phải - Logs"""
        
        # Log Frame
        log_frame = tk.LabelFrame(parent, text="📝 Logs & Thông tin", 
                                 bg='#2d2d2d', fg='white', font=('Arial', 10, 'bold'))
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Text area for logs
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                 bg='#1e1e1e', fg='#00ff00',
                                                 font=('Consolas', 9),
                                                 wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add initial welcome message
        self.log("🚀 Trading Bot GUI đã khởi động!")
        self.log("📊 Đang kết nối với Binance Testnet...")
        self.log("🤖 Đang khởi tạo ChatGPT Advisor...")
        self.log("\n" + "="*60)
        self.log("✅ Bot đã sẵn sàng!")
        self.log("👉 Nhấn 'BẮT ĐẦU' để chạy bot")
        self.log("="*60 + "\n")
        
        # Stats Frame
        stats_frame = tk.Frame(parent, bg='#2d2d2d')
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.total_trades_label = tk.Label(stats_frame, text="Tổng lệnh: 0", 
                                          bg='#2d2d2d', fg='white')
        self.total_trades_label.pack(side=tk.LEFT, padx=10)
        
        self.win_rate_label = tk.Label(stats_frame, text="Win Rate: 0%", 
                                       bg='#2d2d2d', fg='white')
        self.win_rate_label.pack(side=tk.LEFT, padx=10)
        
        self.pnl_label = tk.Label(stats_frame, text="PnL: $0.00", 
                                 bg='#2d2d2d', fg='white')
        self.pnl_label.pack(side=tk.LEFT, padx=10)
    
    def log(self, message):
        """Thêm log vào text area"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def start_bot(self):
        """Bắt đầu bot"""
        if self.running:
            messagebox.showwarning("Cảnh báo", "Bot đang chạy!")
            return
        
        self.running = True
        self.is_demo = False
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.demo_btn.config(state='disabled')
        
        self.log("\n▶️ Bot bắt đầu chạy...")
        self.status_label.config(text="🟢 ĐANG CHẠY", fg='#4CAF50')
        
        # Chạy bot trong thread riêng
        thread = threading.Thread(target=self.run_bot_continuous, daemon=True)
        thread.start()
    
    def stop_bot(self):
        """Dừng bot"""
        self.running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.demo_btn.config(state='normal')
        
        self.log("⏸️ Bot đã dừng")
        self.status_label.config(text="🔴 ĐÃ DỪNG", fg='#f44336')
    
    def run_demo(self):
        """Chạy demo một lần"""
        if self.running:
            messagebox.showwarning("Cảnh báo", "Bot đang chạy!")
            return
        
        self.log("\n🔍 Chạy DEMO (chỉ phân tích)...")
        self.is_demo = True
        
        # Chạy một chu kỳ
        thread = threading.Thread(target=self.run_bot_once, daemon=True)
        thread.start()
    
    def run_bot_once(self):
        """Chạy bot một lần"""
        try:
            result = self.bot.run_once()
            
            if result:
                self.update_info_from_result(result)
        except Exception as e:
            self.log(f"❌ Lỗi: {e}")
            traceback.print_exc()
    
    def run_bot_continuous(self):
        """Chạy bot liên tục"""
        try:
            while self.running:
                self.cycle_count += 1
                self.cycle_label.config(text=f"Chu kỳ: {self.cycle_count}")
                
                self.log(f"\n{'='*60}")
                self.log(f"📊 Chu kỳ #{self.cycle_count}")
                self.log(f"{'='*60}\n")
                
                result = self.bot.run_once()
                
                if result:
                    self.update_info_from_result(result)
                
                # Đợi 15 phút trước chu kỳ tiếp theo
                self.log(f"⏰ Chờ 15 phút đến chu kỳ tiếp theo...")
                for i in range(900):  # 15 phút = 900 giây
                    if not self.running:
                        break
                    time.sleep(1)
                    if i % 60 == 0:  # Mỗi phút
                        self.log(f"⏳ Đang chờ... ({i//60}/15 phút)")
                
        except Exception as e:
            self.log(f"❌ Lỗi chạy bot: {e}")
            traceback.print_exc()
            self.stop_bot()
    
    def update_info_from_result(self, result):
        """Cập nhật thông tin từ kết quả phân tích"""
        try:
            # Cập nhật giá và chỉ số
            if 'price' in result:
                self.price_label.config(text=f"Giá: ${result['price']:.2f}")
            if 'ma' in result:
                self.ma_label.config(text=f"MA(20): ${result['ma']:.2f}")
            if 'rsi' in result:
                self.rsi_label.config(text=f"RSI(14): {result['rsi']:.2f}")
            if 'atr' in result:
                self.atr_label.config(text=f"ATR(14): ${result['atr']:.2f}")
            
            # Cập nhật khuyến nghị
            if 'recommendation' in result:
                rec = result['recommendation']
                color = '#00ff00' if rec == 'BUY' else '#ff0000' if rec == 'SELL' else '#ffff00'
                self.recommendation_label.config(text=f"Khuyến nghị: {rec}", fg=color)
            
            # Cập nhật thời gian
            self.last_update_label.config(text=f"Cập nhật: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.log(f"⚠️ Lỗi cập nhật info: {e}")
    
    def update_info(self):
        """Cập nhật thông tin (placeholder)"""
        pass

