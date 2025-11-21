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
        self.is_demo = False
        self.cycle_count = 0
        self.chat_history = self._init_chat_history()
        
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
        
        # Khu vực cuộn cho các thống kê
        scroll_area = tk.Frame(report_container, bg='#2d2d2d')
        scroll_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        canvas = tk.Canvas(scroll_area, bg='#1e1e1e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_area, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1e1e1e')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.report_frame = scrollable_frame
        self.report_canvas = canvas
        
        # Frame cho biểu đồ
        chart_frame = tk.LabelFrame(report_container, text="📈 Biểu Đồ", 
                                   bg='#2d2d2d', fg='white', font=('Arial', 10, 'bold'))
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.chart_frame = chart_frame
        
        # Load báo cáo ban đầu
        self.refresh_report()
    
    def log(self, message):
        """Thêm log vào text area"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
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
        
        self.running = True
        self.is_demo = False
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.demo_btn.config(state='disabled')
        
        self.log("\n▶️ Bot bắt đầu chạy - CHẾ ĐỘ GIAO DỊCH THẬT")
        self.log("⚠️ Bot sẽ thực hiện lệnh BUY/SELL khi đủ điều kiện")
        self.status_label.config(text="🟢 ĐANG CHẠY (GIAO DỊCH THẬT)", fg='#4CAF50')
        
        # Lấy interval từ config
        import config
        self.bot.trading_interval = config.TRADING_INTERVAL_MINUTES
        
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
                    # Sinh báo cáo sau mỗi chu kỳ
                    try:
                        self.bot.reporting.generate_summary_report()
                        self.bot.reporting.plot_equity_curve()
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
            
            # Tạo frame cho các thống kê
            stats_container = tk.Frame(self.report_frame, bg='#1e1e1e')
            stats_container.pack(fill=tk.X, padx=20, pady=10)
            
            # Hiển thị từng thống kê
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
            
            for i, (label, value, color) in enumerate(stats):
                stat_frame = tk.Frame(stats_container, bg='#2d2d2d', relief=tk.RAISED, bd=2)
                stat_frame.grid(row=i//2, column=i%2, padx=10, pady=5, sticky='ew')
                stats_container.grid_columnconfigure(i%2, weight=1)
                
                label_widget = tk.Label(stat_frame, text=label, 
                                       bg='#2d2d2d', fg='#aaaaaa',
                                       font=('Arial', 9))
                label_widget.pack(pady=5)
                
                value_widget = tk.Label(stat_frame, text=value,
                                       bg='#2d2d2d', fg=color,
                                       font=('Arial', 16, 'bold'))
                value_widget.pack(pady=5)
            
            # Cập nhật canvas scroll
            self.report_canvas.update_idletasks()
            self.report_canvas.configure(scrollregion=self.report_canvas.bbox("all"))
            
            # Cập nhật biểu đồ
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
        self.chat_input.bind('<Return>', lambda event: self.send_chat_message())

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
            
            # Kiểm tra file biểu đồ
            chart_file = config.EQUITY_CURVE_FILE
            if os.path.exists(chart_file):
                self._render_chart_image(chart_file)
            else:
                # Nếu chưa có biểu đồ, tạo từ dữ liệu
                try:
                    self.bot.reporting.plot_equity_curve()
                    if os.path.exists(chart_file):
                        self._render_chart_image(chart_file)
                    else:
                        no_data_label = tk.Label(self.chart_frame,
                                               text="⚠️ Chưa có dữ liệu để vẽ biểu đồ\nHãy chạy bot ít nhất một chu kỳ",
                                               bg='#2d2d2d', fg='#ffff00',
                                               font=('Arial', 12))
                        no_data_label.pack(pady=20)
                except Exception as e:
                    no_data_label = tk.Label(self.chart_frame,
                                           text=f"⚠️ Không thể tạo biểu đồ: {e}",
                                           bg='#2d2d2d', fg='#ff0000',
                                           font=('Arial', 12))
                    no_data_label.pack(pady=20)
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
        self.report_canvas.update_idletasks()
        
        available_width = self.chart_frame.winfo_width()
        if available_width <= 0:
            available_width = self.report_canvas.winfo_width()
        if available_width <= 0:
            available_width = config.REPORT_CHART_MAX_WIDTH
        available_width = max(0, available_width - 40)  # trừ padding khi có
        
        target_width = min(available_width, config.REPORT_CHART_MAX_WIDTH)
        target_width = max(config.REPORT_CHART_MIN_WIDTH, target_width)
        
        # Giữ đúng tỉ lệ ảnh
        aspect_ratio = img.width / img.height if img.height else 1
        target_height = int(target_width / aspect_ratio) if aspect_ratio else config.REPORT_CHART_MAX_HEIGHT
        
        if target_height > config.REPORT_CHART_MAX_HEIGHT:
            target_height = config.REPORT_CHART_MAX_HEIGHT
            target_width = int(target_height * aspect_ratio) if aspect_ratio else target_width
        
        img = img.resize((int(target_width), int(target_height)), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        chart_label = tk.Label(self.chart_frame, image=photo, bg='#2d2d2d')
        chart_label.image = photo  # tránh bị GC
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

