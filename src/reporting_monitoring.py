"""
Module Reporting & Monitoring
- Tạo báo cáo hiệu suất
- Vẽ biểu đồ vốn (equity curve)
- Dashboard giám sát
- Phân tích kết quả giao dịch
"""

import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import os
from . import config


class ReportingMonitoring:
    """
    Class tạo báo cáo và giám sát
    
    Chức năng:
    1. Tạo báo cáo hiệu suất
    2. Vẽ biểu đồ equity curve
    3. Phân tích kết quả giao dịch
    4. Xuất báo cáo ra file
    """
    
    def __init__(self, db_file=None):
        """
        Khởi tạo Reporting & Monitoring
        
        Args:
            db_file: Đường dẫn file database (mặc định từ config)
        """
        self.db_file = db_file or config.DATABASE_FILE
        print("✅ Reporting & Monitoring đã sẵn sàng")
    
    def generate_performance_report(self, days=7):
        """
        Tạo báo cáo hiệu suất
        
        Args:
            days: Số ngày cần báo cáo
        
        Returns:
            dict: Báo cáo hiệu suất
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Lấy tất cả giao dịch có entry_price > 0 (bao gồm cả chưa đóng)
            cursor.execute('''
                SELECT 
                    timestamp,
                    pnl,
                    entry_price,
                    quantity,
                    side
                FROM trading_history
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                AND entry_price > 0
                ORDER BY timestamp ASC
            ''', (days,))
            
            all_trades = cursor.fetchall()
            
            # Tính unrealized PnL cho các giao dịch chưa đóng
            realized_pnl = 0
            unrealized_pnl = 0
            winning_trades = 0
            losing_trades = 0
            closed_trades = 0
            
            # Lấy giá hiện tại để tính unrealized PnL
            try:
                from .trade_executor import TradeExecutor
                temp_executor = TradeExecutor()
                ticker = temp_executor.client.get_symbol_ticker(symbol='BTCUSDT')
                current_price = float(ticker['price']) if ticker else 0.0
            except:
                current_price = 0.0
            
            for trade in all_trades:
                timestamp, pnl, entry_price, quantity, side = trade
                
                if pnl is not None:
                    # Giao dịch đã đóng
                    closed_trades += 1
                    realized_pnl += pnl
                    if pnl > 0:
                        winning_trades += 1
                    elif pnl < 0:
                        losing_trades += 1
                elif current_price > 0 and entry_price > 0:
                    # Giao dịch chưa đóng - tính unrealized PnL
                    if side == 'BUY':
                        unrealized = (current_price - entry_price) * quantity
                    else:  # SELL
                        unrealized = (entry_price - current_price) * quantity
                    unrealized_pnl += unrealized
            
            total_trades = len(all_trades)
            total_pnl = realized_pnl + unrealized_pnl
            
            # Tính thống kê từ các giao dịch đã đóng
            if closed_trades > 0:
                cursor.execute('''
                    SELECT 
                        AVG(CASE WHEN pnl > 0 THEN pnl END) as avg_win,
                        AVG(CASE WHEN pnl < 0 THEN pnl END) as avg_loss
                    FROM trading_history
                    WHERE timestamp >= datetime('now', '-' || ? || ' days')
                    AND pnl IS NOT NULL
                ''', (days,))
                avg_stats = cursor.fetchone()
                avg_win = avg_stats[0] or 0
                avg_loss = avg_stats[1] or 0
                win_rate = (winning_trades / closed_trades * 100) if closed_trades > 0 else 0
                profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
            else:
                avg_win = 0
                avg_loss = 0
                win_rate = 0
                profit_factor = 0
            
            # Lấy số dư tài khoản mới nhất
            cursor.execute('''
                SELECT account_balance FROM performance
                ORDER BY timestamp DESC LIMIT 1
            ''')
            
            latest_balance = cursor.fetchone()
            account_balance = latest_balance[0] if latest_balance else 10000
            
            conn.close()
            
            report = {
                'period_days': days,
                'total_trades': total_trades,
                'closed_trades': closed_trades,
                'open_trades': total_trades - closed_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': round(win_rate, 2),
                'total_pnl': round(total_pnl, 2),
                'realized_pnl': round(realized_pnl, 2),
                'unrealized_pnl': round(unrealized_pnl, 2),
                'avg_win': round(avg_win, 2),
                'avg_loss': round(avg_loss, 2),
                'profit_factor': round(profit_factor, 2),
                'account_balance': account_balance,
                'return_percent': round((total_pnl / account_balance * 100), 2) if account_balance > 0 else 0
            }
            
            return report
            
        except Exception as e:
            print(f"❌ Lỗi tạo báo cáo: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def plot_equity_curve(self, output_file=None):
        if output_file is None:
            output_file = config.EQUITY_CURVE_FILE
        """
        Vẽ biểu đồ equity curve (đường cong vốn)
        
        Args:
            output_file: Tên file output
        """
        try:
            conn = sqlite3.connect(self.db_file)
            
            # Thử đọc từ bảng performance trước (nếu có)
            query_perf = '''
                SELECT 
                    timestamp,
                    account_balance,
                    total_pnl
                FROM performance
                ORDER BY timestamp ASC
            '''
            df_perf = pd.read_sql_query(query_perf, conn)
            
            # Nếu không có dữ liệu trong performance, tính từ trading_history
            if df_perf.empty:
                # Lấy dữ liệu từ trading_history (bao gồm cả lệnh chưa có PnL)
                query_trades = '''
                    SELECT 
                        timestamp,
                        pnl,
                        entry_price,
                        quantity,
                        side
                    FROM trading_history
                    WHERE entry_price > 0
                    ORDER BY timestamp ASC
                '''
                df_trades = pd.read_sql_query(query_trades, conn)
                
                if df_trades.empty:
                    print("⚠️ Không có dữ liệu để vẽ biểu đồ")
                    conn.close()
                    return
                
                # Tính equity curve từ các giao dịch
                # Giả sử số dư ban đầu là 10000 (có thể lấy từ config hoặc database)
                initial_balance = 10000.0
                df_trades['timestamp'] = pd.to_datetime(df_trades['timestamp'])
                df_trades = df_trades.sort_values('timestamp')
                
                # Nếu có PnL, dùng PnL; nếu không, tính unrealized PnL từ entry_price và giá hiện tại
                if df_trades['pnl'].notna().any():
                    # Có PnL thực tế
                    df_trades['pnl_used'] = df_trades['pnl'].fillna(0)
                else:
                    # Tính unrealized PnL: lấy giá hiện tại từ ticker
                    try:
                        from .trade_executor import TradeExecutor
                        temp_executor = TradeExecutor()
                        ticker = temp_executor.client.get_symbol_ticker(symbol='BTCUSDT')
                        current_price = float(ticker['price']) if ticker else 0.0
                        
                        # Tính unrealized PnL
                        def calc_unrealized_pnl(row):
                            if row['side'] == 'BUY':
                                return (current_price - row['entry_price']) * row['quantity']
                            else:  # SELL
                                return (row['entry_price'] - current_price) * row['quantity']
                        
                        df_trades['pnl_used'] = df_trades.apply(calc_unrealized_pnl, axis=1)
                    except:
                        # Nếu không lấy được giá, dùng 0
                        df_trades['pnl_used'] = 0.0
                
                # Tính cumulative PnL
                df_trades['cumulative_pnl'] = df_trades['pnl_used'].cumsum()
                df_trades['account_balance'] = initial_balance + df_trades['cumulative_pnl']
                df_trades['total_pnl'] = df_trades['pnl_used']
                
                df = df_trades[['timestamp', 'account_balance', 'total_pnl']].copy()
            else:
                df = df_perf
            
            conn.close()
            
            if df.empty:
                print("⚠️ Không có dữ liệu để vẽ biểu đồ")
                return
            
            # Vẽ biểu đồ - chỉ giữ đường cong vốn
            fig, ax1 = plt.subplots(figsize=(14, 8))
            
            # Biểu đồ 1: Equity curve
            if 'account_balance' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                ax1.plot(df['timestamp'], df['account_balance'], color='green', linewidth=3)
                ax1.set_title('📈 Đường Cong Vốn (Equity Curve)', fontsize=18, fontweight='bold')
                ax1.set_xlabel('Thời gian', fontsize=14)
                ax1.set_ylabel('Số dư tài khoản (USDT)', fontsize=14)
                ax1.tick_params(labelsize=12)
                ax1.grid(True, alpha=0.3)
                ax1.fill_between(df['timestamp'], df['account_balance'], alpha=0.3, color='green')
            
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✅ Đã vẽ equity curve: {output_file}")
            
        except Exception as e:
            print(f"❌ Lỗi vẽ biểu đồ: {e}")
    
    def generate_summary_report(self):
        """Tạo báo cáo tổng hợp và in ra console"""
        try:
            report = self.generate_performance_report(days=30)
            
            print("\n" + "="*60)
            print("📊 BÁO CÁO HIỆU SUẤT GIAO DỊCH (30 ngày)")
            print("="*60)
            
            print(f"\n💰 Số dư tài khoản: ${report.get('account_balance', 0):.2f}")
            print(f"📈 Tổng PnL: ${report.get('total_pnl', 0):.2f}")
            if report.get('unrealized_pnl', 0) != 0:
                print(f"   ├─ Realized PnL: ${report.get('realized_pnl', 0):.2f}")
                print(f"   └─ Unrealized PnL: ${report.get('unrealized_pnl', 0):.2f}")
            print(f"📊 Tỷ suất sinh lời: {report.get('return_percent', 0):.2f}%")
            
            print(f"\n🎯 Thống kê giao dịch:")
            print(f"   Tổng lệnh: {report.get('total_trades', 0)}")
            if report.get('open_trades', 0) > 0:
                print(f"   ├─ Đã đóng: {report.get('closed_trades', 0)}")
                print(f"   └─ Đang mở: {report.get('open_trades', 0)}")
            if report.get('closed_trades', 0) > 0:
                print(f"   Thắng: {report.get('winning_trades', 0)}")
                print(f"   Thua: {report.get('losing_trades', 0)}")
                print(f"   Win Rate: {report.get('win_rate', 0):.2f}%")
            
            print(f"\n💵 PnL trung bình:")
            print(f"   Lệnh thắng: ${report.get('avg_win', 0):.2f}")
            print(f"   Lệnh thua: ${report.get('avg_loss', 0):.2f}")
            print(f"   Profit Factor: {report.get('profit_factor', 0):.2f}")
            
            print("\n" + "="*60)
            
            return report
            
        except Exception as e:
            print(f"❌ Lỗi tạo báo cáo tổng hợp: {e}")
            return {}
    
    def export_html_report(self, output_file=None):
        if output_file is None:
            output_file = config.REPORT_HTML_FILE
        """
        Xuất báo cáo ra file HTML
        
        Args:
            output_file: Tên file output
        """
        try:
            report = self.generate_performance_report(days=30)
            
            # Tính toán các giá trị
            total_pnl = report.get('total_pnl', 0)
            pnl_class = 'positive' if total_pnl >= 0 else 'negative'
            return_percent = report.get('return_percent', 0)
            return_class = 'positive' if return_percent >= 0 else 'negative'
            
            # Tạo phần PnL detail
            pnl_detail = ""
            if report.get('unrealized_pnl', 0) != 0:
                pnl_detail = f"<div style='margin-top: 10px; font-size: 14px;'>Realized: ${report.get('realized_pnl', 0):.2f} | Unrealized: ${report.get('unrealized_pnl', 0):.2f}</div>"
            
            # Tạo phần trades detail
            trades_detail = ""
            if report.get('open_trades', 0) > 0:
                trades_detail = f"<div style='margin-top: 10px; font-size: 14px;'>Đã đóng: {report.get('closed_trades', 0)} | Đang mở: {report.get('open_trades', 0)}</div>"
            
            # Tạo phần thống kê giao dịch đã đóng
            closed_stats = ""
            if report.get('closed_trades', 0) > 0:
                closed_stats = f"""
        <div class="stat">
            <div class="stat-label">✅ Lệnh thắng</div>
            <div class="stat-value positive">{report.get('winning_trades', 0)}</div>
        </div>
        
        <div class="stat">
            <div class="stat-label">❌ Lệnh thua</div>
            <div class="stat-value negative">{report.get('losing_trades', 0)}</div>
        </div>
        
        <div class="stat">
            <div class="stat-label">📉 Win Rate</div>
            <div class="stat-value">{report.get('win_rate', 0):.2f}%</div>
        </div>"""
            
            html_content = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Trading Bot Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        .stat {{ background: #f0f0f0; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .stat-label {{ font-weight: bold; color: #666; }}
        .stat-value {{ font-size: 24px; color: #333; }}
        .positive {{ color: #4CAF50; }}
        .negative {{ color: #f44336; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Báo Cáo Hiệu Suất Trading Bot</h1>
        <p><strong>Kỳ báo cáo:</strong> 30 ngày qua</p>
        
        <div class="stat">
            <div class="stat-label">💰 Số dư tài khoản</div>
            <div class="stat-value">${report.get('account_balance', 0):.2f}</div>
        </div>
        
        <div class="stat">
            <div class="stat-label">📈 Tổng PnL</div>
            <div class="stat-value {pnl_class}">${total_pnl:.2f}</div>
            {pnl_detail}
        </div>
        
        <div class="stat">
            <div class="stat-label">📊 Tỷ suất sinh lời</div>
            <div class="stat-value {return_class}">{return_percent:.2f}%</div>
        </div>
        
        <div class="stat">
            <div class="stat-label">🎯 Tổng lệnh giao dịch</div>
            <div class="stat-value">{report.get('total_trades', 0)}</div>
            {trades_detail}
        </div>
        {closed_stats}
        <div class="stat">
            <div class="stat-label">⚖️ Profit Factor</div>
            <div class="stat-value">{report.get('profit_factor', 0):.2f}</div>
        </div>
        
        <hr>
        <p><em>Báo cáo được tạo lúc: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
    </div>
</body>
</html>
            """
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ Đã xuất báo cáo HTML: {output_file}")
            
        except Exception as e:
            print(f"❌ Lỗi xuất HTML: {e}")


if __name__ == '__main__':
    # Test module
    print("🧪 Testing Reporting & Monitoring...")
    
    monitor = ReportingMonitoring()
    
    # Test tạo báo cáo
    print("\n📊 Test tạo báo cáo tổng hợp:")
    monitor.generate_summary_report()
    
    # Test vẽ biểu đồ
    print("\n📈 Test vẽ equity curve:")
    monitor.plot_equity_curve()
    
    # Test xuất HTML
    print("\n💾 Test xuất báo cáo HTML:")
    monitor.export_html_report()

