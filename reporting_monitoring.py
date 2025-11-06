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


class ReportingMonitoring:
    """
    Class tạo báo cáo và giám sát
    
    Chức năng:
    1. Tạo báo cáo hiệu suất
    2. Vẽ biểu đồ equity curve
    3. Phân tích kết quả giao dịch
    4. Xuất báo cáo ra file
    """
    
    def __init__(self, db_file='trading_history.db'):
        """
        Khởi tạo Reporting & Monitoring
        
        Args:
            db_file: Đường dẫn file database
        """
        self.db_file = db_file
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
            
            # Lấy thống kê giao dịch
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                    SUM(pnl) as total_pnl,
                    AVG(CASE WHEN pnl > 0 THEN pnl END) as avg_win,
                    AVG(CASE WHEN pnl < 0 THEN pnl END) as avg_loss
                FROM trading_history
                WHERE timestamp >= datetime('now', '-' || ? || ' days')
                AND pnl IS NOT NULL
            ''', (days,))
            
            stats = cursor.fetchone()
            
            # Lấy số dư tài khoản mới nhất
            cursor.execute('''
                SELECT account_balance FROM performance
                ORDER BY timestamp DESC LIMIT 1
            ''')
            
            latest_balance = cursor.fetchone()
            account_balance = latest_balance[0] if latest_balance else 10000
            
            conn.close()
            
            if stats and stats[0] > 0:
                total_trades = stats[0]
                winning_trades = stats[1] or 0
                losing_trades = stats[2] or 0
                total_pnl = stats[3] or 0
                avg_win = stats[4] or 0
                avg_loss = stats[5] or 0
                
                win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
                
                report = {
                    'period_days': days,
                    'total_trades': total_trades,
                    'winning_trades': winning_trades,
                    'losing_trades': losing_trades,
                    'win_rate': round(win_rate, 2),
                    'total_pnl': round(total_pnl, 2),
                    'avg_win': round(avg_win, 2),
                    'avg_loss': round(avg_loss, 2),
                    'profit_factor': round(profit_factor, 2),
                    'account_balance': account_balance,
                    'return_percent': round((total_pnl / account_balance * 100), 2) if account_balance > 0 else 0
                }
            else:
                report = {
                    'period_days': days,
                    'total_trades': 0,
                    'winning_trades': 0,
                    'losing_trades': 0,
                    'win_rate': 0,
                    'total_pnl': 0,
                    'avg_win': 0,
                    'avg_loss': 0,
                    'profit_factor': 0,
                    'account_balance': account_balance,
                    'return_percent': 0
                }
            
            return report
            
        except Exception as e:
            print(f"❌ Lỗi tạo báo cáo: {e}")
            return {}
    
    def plot_equity_curve(self, output_file='equity_curve.png'):
        """
        Vẽ biểu đồ equity curve (đường cong vốn)
        
        Args:
            output_file: Tên file output
        """
        try:
            conn = sqlite3.connect(self.db_file)
            
            # Lấy dữ liệu equity theo thời gian
            query = '''
                SELECT 
                    timestamp,
                    account_balance,
                    total_pnl
                FROM performance
                ORDER BY timestamp ASC
            '''
            
            df = pd.read_sql_query(query, conn)
            
            conn.close()
            
            if df.empty:
                print("⚠️ Không có dữ liệu để vẽ biểu đồ")
                return
            
            # Vẽ biểu đồ
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
            
            # Biểu đồ 1: Equity curve
            if 'account_balance' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                ax1.plot(df['timestamp'], df['account_balance'], color='green', linewidth=2)
                ax1.set_title('📈 Equity Curve (Đường Cong Vốn)', fontsize=14, fontweight='bold')
                ax1.set_xlabel('Thời gian')
                ax1.set_ylabel('Số dư (USDT)')
                ax1.grid(True, alpha=0.3)
                ax1.fill_between(df['timestamp'], df['account_balance'], alpha=0.3, color='green')
            
            # Biểu đồ 2: PnL theo thời gian
            if 'total_pnl' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                colors = ['green' if x > 0 else 'red' for x in df['total_pnl']]
                ax2.bar(df['timestamp'], df['total_pnl'], color=colors, alpha=0.7)
                ax2.axhline(y=0, color='black', linestyle='--', linewidth=1)
                ax2.set_title('📊 PnL theo thời gian', fontsize=14, fontweight='bold')
                ax2.set_xlabel('Thời gian')
                ax2.set_ylabel('PnL (USDT)')
                ax2.grid(True, alpha=0.3)
            
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
            print(f"📊 Tỷ suất sinh lời: {report.get('return_percent', 0):.2f}%")
            
            print(f"\n🎯 Thống kê giao dịch:")
            print(f"   Tổng lệnh: {report.get('total_trades', 0)}")
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
    
    def export_html_report(self, output_file='trading_report.html'):
        """
        Xuất báo cáo ra file HTML
        
        Args:
            output_file: Tên file output
        """
        try:
            report = self.generate_performance_report(days=30)
            
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
            <div class="stat-value {'positive' if report.get('total_pnl', 0) >= 0 else 'negative'}">${report.get('total_pnl', 0):.2f}</div>
        </div>
        
        <div class="stat">
            <div class="stat-label">📊 Tỷ suất sinh lời</div>
            <div class="stat-value {'positive' if report.get('return_percent', 0) >= 0 else 'negative'}">{report.get('return_percent', 0):.2f}%</div>
        </div>
        
        <div class="stat">
            <div class="stat-label">🎯 Tổng lệnh giao dịch</div>
            <div class="stat-value">{report.get('total_trades', 0)}</div>
        </div>
        
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
        </div>
        
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

