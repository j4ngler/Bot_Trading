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
import os
import webbrowser
from . import config


class TradingBotGUI:
    """
    Giao diện GUI cho Trading Bot
    """
    
    def __init__(self, root, trading_bot):
        self.root = root
        self.bot = trading_bot
        self.running = False
        self.cycle_count = 0
        self.session_start_time = datetime.now()
        self.equity_history = []
        self.chat_history = self._init_chat_history()
        self.auto_scroll_var = tk.BooleanVar(value=True)
        self.auto_refresh_var = tk.BooleanVar(value=False)
        self.auto_refresh_interval_var = tk.StringVar(value="5")  # phút
        self.cycle_window_var = tk.StringVar(value="All")
        self.log_filter_var = tk.StringVar(value="All")
        self.log_records = []
        self.api_status = {
            "binance": tk.StringVar(value="⏳ Kiểm tra Binance..."),
            "openai": tk.StringVar(value="⏳ Kiểm tra OpenAI...")
        }
        self._auto_refresh_job = None
        
        # Đăng ký callback để bot log vào GUI khi thực thi lệnh
        self.bot.gui_log_callback = self.log
        
        self.setup_gui()
    
    def setup_gui(self):
        """Thiết lập giao diện"""
        self.root.title("🤖 Trading Bot - ChatGPT + Binance Testnet")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Header
        header_frame = tk.Frame(self.root, bg='#2d2d2d', height=60)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = tk.Label(header_frame, 
                              text="🚀 Trading Bot - ChatGPT + Binance Testnet",
                              font=('Arial', 16, 'bold'),
                              bg='#2d2d2d', fg='#00ff00')
        title_label.pack(pady=15)

        status_frame = tk.Frame(header_frame, bg='#2d2d2d')
        status_frame.pack(side=tk.RIGHT, padx=10)
        self.binance_status_label = tk.Label(
            status_frame, textvariable=self.api_status["binance"],
            bg='#2d2d2d', fg='#aaaaaa', font=('Arial', 9, 'bold')
        )
        self.binance_status_label.pack(side=tk.RIGHT, padx=(5, 0))
        self.openai_status_label = tk.Label(
            status_frame, textvariable=self.api_status["openai"],
            bg='#2d2d2d', fg='#aaaaaa', font=('Arial', 9, 'bold')
        )
        self.openai_status_label.pack(side=tk.RIGHT, padx=(5, 0))
        
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

        self.open_report_btn = tk.Button(control_frame, text="📄 MỞ BÁO CÁO",
                                        command=self.open_report,
                                        bg='#9C27B0', fg='white', font=('Arial', 11, 'bold'),
                                        width=20, height=2)
        self.open_report_btn.pack(pady=5)
        
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
    
        # Khởi tạo trạng thái API ban đầu
        self._update_api_status()
    def setup_right_panel(self, parent):
        """Thiết lập panel phải - Logs và Báo cáo (dùng Notebook/Tabs)"""
        
        # Tạo Notebook (tabs)
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Logs
        log_tab = tk.Frame(self.notebook, bg='#2d2d2d')
        self.notebook.add(log_tab, text="📝 Logs")
        self.setup_logs_tab(log_tab)
        
        # Tab 2: Báo cáo
        report_tab = tk.Frame(self.notebook, bg='#2d2d2d')
        self.notebook.add(report_tab, text="📊 Báo Cáo")
        self.setup_report_tab(report_tab)

        # Tab 3: Chat
        chat_tab = tk.Frame(self.notebook, bg='#2d2d2d')
        self.notebook.add(chat_tab, text="💬 Trò chuyện")
        self.setup_chat_tab(chat_tab)
        
        # Stats Frame (dưới tabs)
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
    
    def setup_logs_tab(self, parent):
        """Thiết lập tab Logs"""
        log_frame = tk.LabelFrame(parent, text="📝 Logs & Thông tin", 
                                 bg='#2d2d2d', fg='white', font=('Arial', 10, 'bold'))
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        controls_frame = tk.Frame(log_frame, bg='#2d2d2d')
        controls_frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        clear_btn = tk.Button(
            controls_frame,
            text="🧹 Xóa log",
            command=self.clear_logs,
            bg='#555555',
            fg='white',
            font=('Arial', 9, 'bold')
        )
        clear_btn.pack(side=tk.LEFT)

        auto_scroll_check = tk.Checkbutton(
            controls_frame,
            text="Tự cuộn",
            variable=self.auto_scroll_var,
            onvalue=True,
            offvalue=False,
            bg='#2d2d2d',
            fg='white',
            selectcolor='#2d2d2d',
            activebackground='#2d2d2d',
            font=('Arial', 9)
        )
        auto_scroll_check.pack(side=tk.LEFT, padx=15)

        tk.Label(controls_frame, text="Lọc", bg='#2d2d2d', fg='white', font=('Arial', 9)).pack(side=tk.LEFT, padx=(10, 3))
        filter_options = ["All", "Info", "Warning", "Error", "Success"]
        filter_menu = ttk.Combobox(controls_frame, values=filter_options, textvariable=self.log_filter_var, width=8, state="readonly")
        filter_menu.pack(side=tk.LEFT)
        filter_menu.bind("<<ComboboxSelected>>", lambda _ : self._refresh_log_display())
        
        # Text area for logs
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                 bg='#1e1e1e', fg='#00ff00',
                                                 font=('Consolas', 9),
                                                 wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.tag_config('time', foreground='#9CDCFE')
        self.log_text.tag_config('info', foreground='#E5E5E5')
        self.log_text.tag_config('success', foreground='#7CFC00')
        self.log_text.tag_config('warning', foreground='#FFC857')
        self.log_text.tag_config('error', foreground='#FF6B6B')
        
        # Add initial welcome message
        self.log("🚀 Trading Bot GUI đã khởi động!")
        self.log("📊 Đang kết nối với Binance Testnet...")
        self.log("🤖 Đang khởi tạo ChatGPT Advisor...")
        self.log("\n" + "="*60)
        self.log("✅ Bot đã sẵn sàng!")
        self.log("👉 Nhấn 'BẮT ĐẦU' để chạy bot")
        self.log("="*60 + "\n")
    
    def setup_report_tab(self, parent):
        """Thiết lập tab Báo cáo"""
        # Frame chứa báo cáo
        report_container = tk.Frame(parent, bg='#2d2d2d')
        report_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Nút refresh báo cáo
        refresh_frame = tk.Frame(report_container, bg='#2d2d2d')
        refresh_frame.pack(fill=tk.X, pady=5)
        
        refresh_btn = tk.Button(refresh_frame, text="🔄 Làm mới báo cáo",
                               command=self.refresh_report,
                               bg='#2196F3', fg='white', font=('Arial', 10, 'bold'))
        refresh_btn.pack(side=tk.LEFT, padx=5)

        # Chọn số chu kỳ hiển thị
        tk.Label(refresh_frame, text="Hiển thị", bg='#2d2d2d', fg='white').pack(side=tk.LEFT, padx=(10, 3))
        cycle_options = ["All", "30", "50", "100"]
        cycle_menu = ttk.Combobox(refresh_frame, values=cycle_options, textvariable=self.cycle_window_var, width=5, state="readonly")
        cycle_menu.pack(side=tk.LEFT)
        cycle_menu.bind("<<ComboboxSelected>>", lambda _ : self.update_chart())

        # Auto refresh
        auto_refresh_check = tk.Checkbutton(
            refresh_frame,
            text="Auto refresh",
            variable=self.auto_refresh_var,
            onvalue=True,
            offvalue=False,
            bg='#2d2d2d',
            fg='white',
            selectcolor='#2d2d2d',
            activebackground='#2d2d2d',
            command=self._toggle_auto_refresh
        )
        auto_refresh_check.pack(side=tk.LEFT, padx=(15, 5))
        tk.Label(refresh_frame, text="(phút)", bg='#2d2d2d', fg='white').pack(side=tk.LEFT, padx=(3, 2))
        interval_entry = tk.Entry(refresh_frame, textvariable=self.auto_refresh_interval_var, width=4)
        interval_entry.pack(side=tk.LEFT)
        
        # Khu vực tóm tắt
        self.report_frame = tk.Frame(report_container, bg='#1e1e1e')
        self.report_frame.pack(fill=tk.X, padx=10, pady=(5, 5))
        
        # Frame cho biểu đồ
        chart_frame = tk.LabelFrame(
            report_container,
            text="📈 Biểu Đồ",
            bg='#2d2d2d',
            fg='white',
            font=('Arial', 10, 'bold')
        )
        # Không dùng expand để tránh khung biểu đồ phóng to bất thường khi chưa có dữ liệu
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        chart_frame.config(height=500)
        
        self.chart_frame = chart_frame
        self.chart_update_label = tk.Label(report_container, text="", bg='#2d2d2d', fg='#aaaaaa', font=('Arial', 9, 'italic'))
        self.chart_update_label.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        # Load báo cáo ban đầu
        self.refresh_report()
    
    def log(self, message):
        """Thêm log vào text area"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        tag = self._resolve_log_tag(message)
        self.log_records.append((timestamp, message, tag))
        self._refresh_log_display()

    def clear_logs(self):
        """Xóa toàn bộ log khỏi khung hiển thị"""
        self.log_text.delete('1.0', tk.END)
        self.log_records.clear()

    def _toggle_auto_refresh(self):
        if self.auto_refresh_var.get():
            self._start_auto_refresh()
        else:
            self._cancel_auto_refresh()

    def _start_auto_refresh(self):
        self._cancel_auto_refresh()
        try:
            minutes = float(self.auto_refresh_interval_var.get())
            delay_ms = max(10, int(minutes * 60 * 1000))
        except ValueError:
            delay_ms = 5 * 60 * 1000  # mặc định 5 phút nếu nhập sai

        def job():
            if self.running and self.auto_refresh_var.get():
                self.refresh_report()
                self._auto_refresh_job = self.root.after(delay_ms, job)

        self._auto_refresh_job = self.root.after(delay_ms, job)

    def _cancel_auto_refresh(self):
        if self._auto_refresh_job:
            try:
                self.root.after_cancel(self._auto_refresh_job)
            except Exception:
                pass
            self._auto_refresh_job = None

    def _resolve_log_tag(self, message):
        """Xác định màu log dựa trên nội dung"""
        text = message.upper()
        if any(key in text for key in ['❌', 'LỖI', 'ERROR', 'FAILED']):
            return 'error'
        if any(key in text for key in ['⚠️', 'CẢNH BÁO', 'WARNING']):
            return 'warning'
        if any(key in text for key in ['✅', 'THÀNH CÔNG', 'SUCCESS', 'ĐÃ LƯU']):
            return 'success'
        return 'info'

    def _refresh_log_display(self):
        """Hiển thị log theo bộ lọc hiện tại"""
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        current_filter = self.log_filter_var.get()
        for ts, msg, tag in self.log_records:
            if current_filter != "All":
                if current_filter == "Info" and tag != 'info':
                    continue
                if current_filter == "Warning" and tag != 'warning':
                    continue
                if current_filter == "Error" and tag != 'error':
                    continue
                if current_filter == "Success" and tag != 'success':
                    continue
            self.log_text.insert(tk.END, f"[{ts}] ", ('time',))
            self.log_text.insert(tk.END, f"{msg}\n", (tag,))
        if self.auto_scroll_var.get():
            self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
    
    def start_bot(self):
        """Bắt đầu bot - THỰC HIỆN GIAO DỊCH THẬT"""
        if self.running:
            messagebox.showwarning("Cảnh báo", "Bot đang chạy!")
            return
        
        # Xác nhận với người dùng
        confirm = messagebox.askyesno(
            "Xác nhận", 
            "Bot sẽ thực hiện GIAO DỊCH THẬT trên Binance Testnet.\n\n"
            "⚠️ Đảm bảo bạn đã:\n"
            "- Cấu hình API keys đúng\n"
            "- Hiểu rủi ro (dù là Testnet)\n"
            "- Đã test với DEMO trước\n\n"
            "Tiếp tục?"
        )
        
        if not confirm:
            return
        
        self.session_start_time = datetime.now()
        self.equity_history = []
        self.running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.demo_btn.config(state='disabled')
        
        self.log("\n▶️ Bot bắt đầu chạy - CHẾ ĐỘ GIAO DỊCH THẬT")
        self.log("⚠️ Bot sẽ thực hiện lệnh BUY/SELL khi đủ điều kiện")
        self.status_label.config(text="🟢 ĐANG CHẠY (GIAO DỊCH THẬT)", fg='#4CAF50')
        self._update_api_status()
        
        # Lấy interval từ config
        self.bot.trading_interval = config.TRADING_INTERVAL_MINUTES
        self._start_auto_refresh()
        
        # Chạy bot trong thread riêng
        thread = threading.Thread(target=self.run_bot_continuous, daemon=True)
        thread.start()
    
    def stop_bot(self):
        """Dừng bot"""
        self.running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.demo_btn.config(state='normal')
        self._cancel_auto_refresh()
        
        self.log("⏸️ Bot đã dừng")
        self.status_label.config(text="🔴 ĐÃ DỪNG", fg='#f44336')
    
    def run_demo(self):
        """Chạy demo một lần"""
        if self.running:
            messagebox.showwarning("Cảnh báo", "Bot đang chạy!")
            return
        
        self.log("\n🔍 Chạy DEMO (chỉ phân tích)...")
        
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
        """Chạy bot liên tục - THỰC HIỆN GIAO DỊCH THẬT"""
        try:
            while self.running:
                self.cycle_count += 1
                self.cycle_label.config(text=f"Chu kỳ: {self.cycle_count}")
                
                self.log(f"\n{'='*60}")
                self.log(f"📊 Chu kỳ #{self.cycle_count} - GIAO DỊCH THẬT")
                self.log(f"{'='*60}\n")
                
                result = self.bot.run_once()
                
                if result:
                    self.update_info_from_result(result)
                    
                    # Cập nhật số dư ngay sau khi có lệnh thành công
                    executed = result.get('executed', False)
                    if executed:
                        try:
                            # Lấy số dư thực tế từ Binance API ngay lập tức
                            balances = self.bot.executor.get_account_balance()
                            usdt_balance = balances.get('USDT', 0)
                            btc_balance = balances.get('BTC', 0)
                            
                            # Lấy giá BTC hiện tại
                            try:
                                ticker = self.bot.executor.client.get_symbol_ticker(symbol='BTCUSDT')
                                btc_price = float(ticker['price']) if ticker else 0.0
                                account_balance = usdt_balance + (btc_balance * btc_price)
                            except:
                                account_balance = usdt_balance
                            
                            if account_balance > 0:
                                self.log(f"💰 Số dư hiện tại: ${account_balance:.2f} (USDT: ${usdt_balance:.2f}, BTC: {btc_balance:.6f})")
                        except Exception as e:
                            self.log(f"⚠️ Lỗi lấy số dư: {e}")
                    
                    # Sinh báo cáo sau mỗi chu kỳ
                    try:
                        summary = self.bot.reporting.generate_summary_report()
                        if summary:
                            balance = summary.get('account_balance', 0)
                            rec = result.get('recommendation', '')
                            self.equity_history.append((self.cycle_count, balance, rec))
                        self.bot.reporting.plot_equity_curve(equity_points=self.equity_history)
                        self.bot.reporting.export_html_report()
                        self.log(f"📄 Đã cập nhật báo cáo: {config.REPORT_HTML_FILE}, {config.EQUITY_CURVE_FILE}")
                        # Cập nhật báo cáo trên GUI
                        self.refresh_report()
                    except Exception as e:
                        self.log(f"⚠️ Lỗi tạo báo cáo: {e}")
                
                # Đợi 5 phút trước chu kỳ tiếp theo
                interval_minutes = getattr(self.bot, 'trading_interval', 5)  # Mặc định 5 phút
                interval_seconds = interval_minutes * 60
                self.log(f"⏰ Chờ {interval_minutes} phút đến chu kỳ tiếp theo...")
                for i in range(interval_seconds):
                    if not self.running:
                        break
                    time.sleep(1)
                    if i % 60 == 0:  # Mỗi phút
                        self.log(f"⏳ Đang chờ... ({i//60}/{interval_minutes} phút)")
                
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
    
    def open_report(self):
        """Mở báo cáo HTML trong trình duyệt/ứng dụng mặc định."""
        try:
            output_path = config.REPORT_HTML_FILE
            if not os.path.exists(output_path):
                messagebox.showinfo("Thông báo", "Chưa có báo cáo. Hãy chạy bot ít nhất một chu kỳ để tạo báo cáo.")
                return

            self.log(f"🌐 Đang mở báo cáo {os.path.basename(output_path)}...")
            webbrowser.open_new_tab(os.path.abspath(output_path))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở báo cáo: {e}")
    
    def refresh_report(self):
        """Làm mới báo cáo trên GUI"""
        try:
            # Xóa nội dung cũ
            for widget in self.report_frame.winfo_children():
                widget.destroy()
            
            # Lấy dữ liệu báo cáo
            report = self.bot.reporting.generate_performance_report(days=30)
            
            # Hiển thị báo cáo
            title = tk.Label(self.report_frame, 
                           text="📊 BÁO CÁO HIỆU SUẤT GIAO DỊCH (30 ngày)",
                           bg='#1e1e1e', fg='#00ff00', 
                           font=('Arial', 14, 'bold'))
            title.pack(pady=10)
            
            stats = [
                ("💰 Số dư tài khoản", f"${report.get('account_balance', 0):.2f}", '#00ff00'),
                ("📈 Tổng PnL", f"${report.get('total_pnl', 0):.2f}",
                 '#00ff00' if report.get('total_pnl', 0) >= 0 else '#ff0000'),
                ("📊 Tỷ suất sinh lời", f"{report.get('return_percent', 0):.2f}%",
                 '#00ff00' if report.get('return_percent', 0) >= 0 else '#ff0000'),
                ("🎯 Tổng lệnh", str(report.get('total_trades', 0)), '#ffffff'),
                ("✅ Lệnh thắng", str(report.get('winning_trades', 0)), '#00ff00'),
                ("❌ Lệnh thua", str(report.get('losing_trades', 0)), '#ff0000'),
                ("📉 Win Rate", f"{report.get('win_rate', 0):.2f}%", '#ffff00'),
                ("⚖️ Profit Factor", f"{report.get('profit_factor', 0):.2f}", '#ffffff'),
            ]
            
            summary_row = tk.Frame(self.report_frame, bg='#1e1e1e')
            summary_row.pack(fill=tk.X, padx=10, pady=5)
            
            for label, value, color in stats:
                stat_frame = tk.Frame(summary_row, bg='#2d2d2d', relief=tk.RAISED, bd=2)
                stat_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4, pady=2)
                
                label_widget = tk.Label(
                    stat_frame,
                    text=label,
                    bg='#2d2d2d',
                    fg='#aaaaaa',
                    font=('Arial', 9)
                )
                label_widget.pack(pady=(6, 2))
                
                value_widget = tk.Label(
                    stat_frame,
                    text=value,
                    bg='#2d2d2d',
                    fg=color,
                    font=('Arial', 16, 'bold')
                )
                value_widget.pack(pady=(0, 6))
            
            self.update_chart()
        
            # Cập nhật stats ở dưới (nếu đã khởi tạo)
            self._update_summary_stats(report)
            
        except Exception as e:
            error_label = tk.Label(self.report_frame,
                                 text=f"❌ Lỗi tải báo cáo: {e}",
                                 bg='#1e1e1e', fg='#ff0000',
                                 font=('Arial', 12))
            error_label.pack(pady=20)

    def setup_chat_tab(self, parent):
        """Thiết lập tab trò chuyện với ChatGPT"""
        chat_frame = tk.Frame(parent, bg='#2d2d2d')
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        instruction = tk.Label(
            chat_frame,
            text="💬 Hỏi đáp nhanh với trợ lý AI (Binance Testnet - mục đích học tập).",
            bg='#2d2d2d', fg='#ffffff', font=('Arial', 10, 'italic')
        )
        instruction.pack(anchor='w', pady=(0, 5))

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            bg='#1e1e1e', fg='#00ffcc',
            font=('Consolas', 10),
            wrap=tk.WORD, height=15
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=5)
        self.chat_display.config(state='disabled')

        input_frame = tk.Frame(chat_frame, bg='#2d2d2d')
        input_frame.pack(fill=tk.X, pady=(5, 0))

        self.chat_input = tk.Entry(input_frame, font=('Arial', 11))
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.chat_input.bind('<Return>', lambda _: self.send_chat_message())

        self.send_chat_btn = tk.Button(
            input_frame,
            text="Gửi",
            command=self.send_chat_message,
            bg='#4CAF50', fg='white',
            font=('Arial', 10, 'bold'),
            width=10
        )
        self.send_chat_btn.pack(side=tk.RIGHT)

        if not self.bot or not getattr(self.bot, 'advisor', None):
            self.send_chat_btn.config(state='disabled')
            self._append_chat_message("system", "⚠️ ChatGPT Advisor chưa sẵn sàng. Kiểm tra API key.")
        else:
            self._append_chat_message("system", "🤖 Xin chào! Hỏi mình bất cứ điều gì về bot và thị trường nhé.")
    
    def update_chart(self):
        """Cập nhật biểu đồ equity curve"""
        try:
            # Xóa biểu đồ cũ
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            chart_file = config.EQUITY_CURVE_FILE
            try:
                cycles_to_show = self.cycle_window_var.get()
                if cycles_to_show != "All":
                    try:
                        max_points = int(cycles_to_show)
                    except ValueError:
                        max_points = None
                else:
                    max_points = None

                history = self.equity_history
                if max_points and len(history) > max_points:
                    history = history[-max_points:]

                if not os.path.exists(chart_file) or not history:
                    self.bot.reporting.plot_equity_curve(equity_points=history)
                if os.path.exists(chart_file):
                    self._render_chart_image(chart_file)
                else:
                    no_data_label = tk.Label(
                        self.chart_frame,
                        text="⚠️ Chưa có dữ liệu để vẽ biểu đồ\nHãy chạy bot ít nhất một chu kỳ",
                        bg='#2d2d2d',
                        fg='#ffff00',
                        font=('Arial', 12)
                    )
                    no_data_label.pack(pady=20)
            except Exception as e:
                no_data_label = tk.Label(
                    self.chart_frame,
                    text=f"⚠️ Không thể tạo biểu đồ: {e}",
                    bg='#2d2d2d',
                    fg='#ff0000',
                    font=('Arial', 12)
                )
                no_data_label.pack(pady=20)
            self.chart_update_label.config(text=f"Cập nhật: {datetime.now().strftime('%H:%M:%S')}")
        except ImportError:
            # Nếu không có PIL, hiển thị thông báo
            no_pil_label = tk.Label(self.chart_frame,
                                  text="⚠️ Cần cài Pillow để hiển thị biểu đồ\npip install Pillow",
                                  bg='#2d2d2d', fg='#ffff00',
                                  font=('Arial', 12))
            no_pil_label.pack(pady=20)
        except Exception as e:
            error_label = tk.Label(self.chart_frame,
                                  text=f"❌ Lỗi hiển thị biểu đồ: {e}",
                                  bg='#2d2d2d', fg='#ff0000',
                                  font=('Arial', 12))
            error_label.pack(pady=20)

    def _render_chart_image(self, chart_file):
        """Render ảnh biểu đồ với kích cỡ linh hoạt theo khung"""
        from PIL import Image, ImageTk
        img = Image.open(chart_file)
        
        # Đảm bảo khung đã cập nhật kích thước trước khi lấy width
        self.chart_frame.update_idletasks()
        
        available_width = self.chart_frame.winfo_width()
        if available_width <= 0:
            available_width = config.REPORT_CHART_MAX_WIDTH
        available_width = max(0, available_width - 40)  # trừ padding khi có
        
        target_width = min(available_width, config.REPORT_CHART_MAX_WIDTH)
        target_width = max(config.REPORT_CHART_MIN_WIDTH, target_width)
        
        # Giữ đúng tỉ lệ ảnh
        aspect_ratio = img.width / img.height if img.height else 1
        target_height = int(target_width / aspect_ratio) if aspect_ratio else config.REPORT_CHART_MAX_HEIGHT
        
        max_height = getattr(config, 'REPORT_CHART_TARGET_HEIGHT', config.REPORT_CHART_MAX_HEIGHT)
        target_height = min(target_height, max_height)
        if target_height > config.REPORT_CHART_MAX_HEIGHT:
            target_height = config.REPORT_CHART_MAX_HEIGHT
            target_width = int(target_height * aspect_ratio) if aspect_ratio else target_width
        
        img = img.resize((int(target_width), int(target_height)), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        if not hasattr(self, '_chart_photo_refs'):
            self._chart_photo_refs = []
        self._chart_photo_refs[:] = [photo]  # giữ tham chiếu tránh GC
        
        chart_label = tk.Label(self.chart_frame, image=photo, bg='#2d2d2d')
        chart_label.pack(pady=10)

    def _init_chat_history(self):
        """Khởi tạo lịch sử chat cho ChatGPT"""
        if not self.bot or not getattr(self.bot, 'advisor', None):
            return None
        return [{
            "role": "system",
            "content": (
                "Bạn là trợ lý giao dịch AI thân thiện, dùng tiếng Việt dễ hiểu cho học sinh cấp 3. "
                "Giải thích rõ ràng, nhắc người dùng đây là môi trường học tập trên Binance Testnet "
                "và không đưa lời khuyên đầu tư thực tế."
            )
        }]

    def _append_chat_message(self, role, message):
        """Hiển thị tin nhắn trên khung chat"""
        if not hasattr(self, 'chat_display'):
            return
        self.chat_display.config(state='normal')
        prefix = "Bạn" if role == "user" else ("AI" if role == "assistant" else "Hệ thống")
        self.chat_display.insert(tk.END, f"{prefix}: {message}\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')

    def _update_api_status(self):
        """Cập nhật badge trạng thái kết nối API"""
        # Kiểm tra Binance
        binance_ok = hasattr(self.bot, 'executor') and self.bot.executor is not None
        binance_text = "Binance: OK" if binance_ok else "Binance: Lỗi"
        binance_color = '#00ff00' if binance_ok else '#ff5555'
        self.api_status["binance"].set(binance_text)
        if hasattr(self, 'binance_status_label'):
            self.binance_status_label.config(fg=binance_color)

        # Kiểm tra OpenAI
        openai_ok = hasattr(self.bot, 'advisor') and self.bot.advisor is not None and getattr(self.bot.advisor, 'model', None)
        openai_text = "OpenAI: OK" if openai_ok else "OpenAI: Lỗi"
        openai_color = '#00ff00' if openai_ok else '#ff5555'
        self.api_status["openai"].set(openai_text)
        if hasattr(self, 'openai_status_label'):
            self.openai_status_label.config(fg=openai_color)

    def send_chat_message(self):
        """Gửi câu hỏi tới ChatGPT"""
        if not self.chat_history:
            messagebox.showwarning("Thông báo", "ChatGPT Advisor chưa sẵn sàng.")
            return

        user_message = self.chat_input.get().strip()
        if not user_message:
            return

        self.chat_input.delete(0, tk.END)
        self._append_chat_message("user", user_message)

        self.send_chat_btn.config(state='disabled')

        def worker():
            try:
                reply = self.bot.advisor.chat_with_user(self.chat_history, user_message)
                self.root.after(0, lambda: self._handle_chat_response(reply))
            except Exception as e:
                self.root.after(0, lambda: self._handle_chat_error(e))

        threading.Thread(target=worker, daemon=True).start()

    def _handle_chat_response(self, reply):
        """Hiển thị phản hồi từ ChatGPT"""
        self._append_chat_message("assistant", reply)
        self.send_chat_btn.config(state='normal')
        self.chat_input.focus_set()

    def _handle_chat_error(self, error):
        """Thông báo khi chat lỗi"""
        self._append_chat_message("system", f"❌ Lỗi trò chuyện: {error}")
        self.send_chat_btn.config(state='normal')
        self.chat_input.focus_set()

    def _update_summary_stats(self, report):
        """Cập nhật các nhãn tổng hợp dưới tab"""
        if not hasattr(self, 'total_trades_label'):
            return
        self.total_trades_label.config(text=f"Tổng lệnh: {report.get('total_trades', 0)}")
        self.win_rate_label.config(text=f"Win Rate: {report.get('win_rate', 0):.2f}%")
        pnl = report.get('total_pnl', 0)
        pnl_color = '#00ff00' if pnl >= 0 else '#ff0000'
        self.pnl_label.config(text=f"PnL: ${pnl:.2f}", fg=pnl_color)

