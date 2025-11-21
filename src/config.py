"""
File cấu hình cho Trading Bot
Học sinh cần điền thông tin API key của mình
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============ BINANCE TESTNET API ============
BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', 'your_testnet_api_key_here')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY', 'your_testnet_secret_key_here')

# Testnet endpoints (SAFE - không dùng tiền thật)
BINANCE_TESTNET_URL = 'https://testnet.binance.vision'
BINANCE_SPOT_TESTNET_URL = 'https://testnet.binance.vision/api'

# ============ OPENAI CHATGPT API ============
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')

# Model: dùng gpt-4o-mini để tiết kiệm, hoặc gpt-4o
OPENAI_MODEL = 'gpt-4o-mini'

# ============ TRADING CONFIGURATION ============
# Symbol để trade
TRADE_SYMBOL = 'BTCUSDT'

# Khung thời gian
INTERVALS = ['1m', '5m', '15m', '1h']

# Chỉ số kỹ thuật
MA_PERIOD = 15          # Moving Average
RSI_PERIOD = 14         # RSI
ATR_PERIOD = 14         # ATR

# Quản lý rủi ro
RISK_PERCENTAGE = 1.0   # Rủi ro 1% vốn mỗi lệnh
STOP_LOSS_PERCENT = 2.0 # Stop loss 2%
TAKE_PROFIT_PERCENT = 3.0 # Take profit 3%
# Ngưỡng ATR so với giá để chặn biến động quá lớn (mặc định 25%)
ATR_VOLATILITY_THRESHOLD = float(os.getenv('ATR_VOLATILITY_THRESHOLD', '0.25'))

# Số lượng tối đa lệnh mở
MAX_POSITIONS = 1

# Chu kỳ phân tích (phút)
TRADING_INTERVAL_MINUTES = 5  # Mặc định 5 phút (đã rút ngắn từ 15 phút)

# ============ LOGGING & REPORTING ============
# Đường dẫn thư mục data (tương đối từ project root)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
# Đảm bảo thư mục data tồn tại
os.makedirs(DATA_DIR, exist_ok=True)
LOG_FILE = os.path.join(DATA_DIR, 'trading_logs.txt')
DATABASE_FILE = os.path.join(DATA_DIR, 'trading_history.db')
REPORT_HTML_FILE = os.path.join(DATA_DIR, 'trading_report.html')
EQUITY_CURVE_FILE = os.path.join(DATA_DIR, 'duong_cong_von.png')
# Kích cỡ biểu đồ trên tab báo cáo (px)
REPORT_CHART_MIN_WIDTH = int(os.getenv('REPORT_CHART_MIN_WIDTH', '600'))
REPORT_CHART_MAX_WIDTH = int(os.getenv('REPORT_CHART_MAX_WIDTH', '1400'))
REPORT_CHART_MAX_HEIGHT = int(os.getenv('REPORT_CHART_MAX_HEIGHT', '650'))

# Dashboard port (cho Plotly Dash)
DASHBOARD_PORT = 8050

# ============ PROMPT CHO CHATGPT ============
TRADING_PROMPT = """
Bạn là một chuyên gia phân tích thị trường tiền điện tử. 
Dựa trên dữ liệu kỹ thuật sau, hãy đưa ra khuyến nghị:

Symbol: {symbol}
Giá hiện tại: ${current_price}
Moving Average ({ma_period}): {ma_value}
RSI: {rsi_value}
ATR: {atr_value}

Yêu cầu:
1. Phân tích tình hình thị trường (giá đang trong xu hướng nào?)
2. RSI cho thấy gì? (quá mua/quá bán?)
3. MA cho thấy gì? (kháng cự/hỗ trợ?)
4. ATR cho thấy biến động như thế nào?

KHÔNG ĐƯỢC đưa ra khuyến nghị cụ thể Mua/Bán.
Chỉ phân tích dữ liệu và giải thích ý nghĩa.

Trả lời bằng tiếng Việt, ngắn gọn (3-4 câu).
"""

SIMPLE_PROMPT = """
Dựa trên dữ liệu: MA={ma}, RSI={rsi}, ATR={atr}
Cho BTC/USDT, khuyến nghị: BUY / SELL / HOLD?

Chỉ trả lời: BUY, SELL, hoặc HOLD
"""

