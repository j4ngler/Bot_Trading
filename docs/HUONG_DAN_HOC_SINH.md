# 📘 Hướng Dẫn Chi Tiết - Trading Bot

> Dành cho Học Sinh Cấp 3 - Bắt Đầu Từ Số Không

---

## 🎯 Dự Án Này Là Gì?

Đây là một **trading bot tự động** - một chương trình máy tính có thể:
- Theo dõi giá Bitcoin
- Phân tích xu hướng
- Quyết định MUA hoặc BÁN
- **Dùng AI (ChatGPT)** để đưa ra khuyến nghị

**⚠️ QUAN TRỌNG**: Bot này **CHỈ dùng Testnet** (tiền giả) - AN TOÀN 100%!

---

## 📚 Phần 1: Kiến Thức Cơ Bản

### 1.1 Trading Là Gì?

**Trading** = Mua/Bán để kiếm lời từ sự chênh lệch giá

Ví dụ:
```
Mua BTC ở: $40,000
Bán BTC ở:  $42,000
Lời:        $2,000 (5%)
```

### 1.2 Chỉ Báo Kỹ Thuật

#### RSI (Relative Strength Index)
- **Công dụng**: Đo xem thị trường "quá mua" hay "quá bán"
- **RSI > 70**: Quá mua → Có thể giảm sớm
- **RSI < 30**: Quá bán → Có thể tăng
- **RSI 30-70**: Bình thường

#### MA (Moving Average)
- **Công dụng**: Đường trung bình giá
- **Giá > MA**: Xu hướng TĂNG
- **Giá < MA**: Xu hướng GIẢM
- **Ví dụ**: MA(20) = Trung bình 20 phiên gần nhất

#### ATR (Average True Range)
- **Công dụng**: Đo biến động giá
- **ATR cao**: Giá nhảy mạnh → Cần stop loss xa hơn
- **ATR thấp**: Giá ổn định → Stop loss gần hơn

### 1.3 ChatGPT API

ChatGPT không chỉ chat, mà còn:
- **Phân tích dữ liệu**
- **Đưa ra khuyến nghị** (Mua/Bán/Giữ)
- **Giải thích lý do** rõ ràng

---

## 🔧 Phần 2: Cài Đặt

### 2.1 Cài Python

1. Tải Python: https://www.python.org/downloads/
2. Cài đặt (tick "Add Python to PATH")
3. Kiểm tra:
   ```bash
   python --version
   ```

### 2.2 Cài Thư Viện

```bash
pip install python-binance openai pandas pandas-ta
```

### 2.3 Đăng Ký API Keys

#### A. Binance Testnet (MIỄN PHÍ)

1. Truy cập: https://testnet.binance.vision/
2. Đăng ký account
3. Vào "API Management"
4. Tạo API Key mới
5. Copy key và secret

#### B. OpenAI API (CÓ PHÍ)

1. Truy cập: https://platform.openai.com
2. Đăng ký + nạp tiền ($5-10)
3. Vào "API keys"
4. Tạo key mới
5. Copy key (dạng: `sk-...`)

### 2.4 Cấu Hình

Tạo file `.env`:

```bash
BINANCE_API_KEY=your_testnet_key
BINANCE_SECRET_KEY=your_secret
OPENAI_API_KEY=sk-your_openai_key
```

---

## 💻 Phần 3: Hiểu Code

### 3.1 File `main.py` - Điều Khiển Chính

```python
# Khởi tạo bot
bot = TradingBot()

# Chạy 1 lần
bot.run_once()

# Hoặc chạy liên tục
bot.run_continuous()
```

### 3.2 Luồng Hoạt Động

```
1. Thu thập dữ liệu
   ↓
2. Tính RSI, MA, ATR
   ↓
3. Gửi cho ChatGPT phân tích
   ↓
4. Nhận khuyến nghị (BUY/SELL/HOLD)
   ↓
5. Thực thi lệnh (nếu hợp lý)
   ↓
6. Ghi log kết quả
```

### 3.3 File `data_collector.py`

**Chức năng**: Lấy dữ liệu từ Binance

```python
# Lấy giá hiện tại
price = collector.get_current_price('BTCUSDT')
print(f"Giá: ${price}")

# Lấy dữ liệu nến
candles = collector.get_candles('BTCUSDT', '15m', limit=100)
```

### 3.4 File `technical_indicators.py`

**Chức năng**: Tính các chỉ số

```python
# Tính RSI
rsi = TechnicalIndicators.calculate_rsi(df, period=14)
print(f"RSI: {rsi.iloc[-1]}")

# Tính tất cả
indicators = TechnicalIndicators.get_all_indicators(df)
```

### 3.5 File `chatgpt_advisor.py`

**Chức năng**: Dùng AI phân tích

```python
advice = advisor.analyze_market(
    symbol='BTCUSDT',
    current_price=43250,
    ma=42800,
    rsi=72,
    atr=250
)

print(advice['recommendation'])  # BUY/SELL/HOLD
print(advice['reason'])         # Lý do
```

### 3.6 File `trade_executor.py`

**Chức năng**: Đặt lệnh giao dịch

```python
# Tính số lượng
quantity = executor.calculate_quantity(price=43250, risk=1.0)

# Mua
executor.place_market_buy('BTCUSDT', quantity)

# Bán
executor.place_market_sell('BTCUSDT', quantity)
```

---

## 🎨 Phần 4: Tùy Chỉnh

### 4.1 Thay Đổi Symbol

Sửa trong `config.py`:

```python
TRADE_SYMBOL = 'ETHUSDT'  # Thay BTCUSDT thành ETHUSDT
```

### 4.2 Thay Đổi Rủi Ro

```python
RISK_PERCENTAGE = 0.5  # Giảm từ 1% xuống 0.5%
```

### 4.3 Thay Đổi Chu Kỳ

```python
MA_PERIOD = 50  # Thay vì 20
RSI_PERIOD = 21  # Thay vì 14
```

### 4.4 Tắt Tự Động Giao Dịch

Chỉ phân tích, không giao dịch:

```python
# Trong main.py
should_execute = False  # Luôn False
```

---

## 📊 Phần 5: Hiểu Kết Quả

### Output Mẫu

```
📊 Chu kỳ phân tích - 14:30:15
==================================================

1️⃣ Thu thập dữ liệu từ Binance...
✅ Lấy được 100 candle 15m cho BTCUSDT

2️⃣ Tính toán chỉ báo kỹ thuật...
   💰 Giá hiện tại: $43,250.50
   📈 MA(20): $42,800.00
   📊 RSI(14): 72.50
   📉 ATR(14): $250.00
   ⚠️ RSI QUÁ MUA - Thị trường có thể giảm

3️⃣ ChatGPT đang phân tích...
🤖 KHUYẾN NGHỊ: SELL
💬 Lý do: RSI cao cho thấy thị trường quá mua...

4️⃣ Kiểm tra điều kiện...
⚠️ RSI quá cực - Không an toàn
⏸️ Tạm thời GIỮ - Không giao dịch
```

### Giải Thích

- **Giá hiện tại**: $43,250
- **MA**: $42,800 → Giá đang trên MA (tăng)
- **RSI**: 72.5 → Quá mua (nguy hiểm)
- **Khuyến nghị**: SELL → Nên bán
- **Kết quả**: Không thực thi (RSI quá cao)

---

## 🧪 Phần 6: Test & Demo

### Test Module Đơn Lẻ

```bash
# Test data collector
python data_collector.py

# Test indicators
python technical_indicators.py

# Test ChatGPT
python chatgpt_advisor.py

# Test executor
python trade_executor.py
```

### Demo Không Giao Dịch

Chỉnh trong `main.py`:

```python
# Thay đổi này
should_execute = True
# Thành
should_execute = False
```

---

## 🎓 Phần 7: Bài Tập Thực Hành

### Bài 1: Thêm Indicator Mới

**Nhiệm vụ**: Thêm MACD vào `technical_indicators.py`

**Gợi ý**:
```python
def calculate_macd(df, fast=12, slow=26, signal=9):
    macd = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
    return macd
```

### Bài 2: Thay Đổi Prompt ChatGPT

**Nhiệm vụ**: Sửa prompt trong `config.py` để ChatGPT trả lời khác đi

**Ví dụ**: Thêm "Hãy phân tích theo phong cách Warren Buffett"

### Bài 3: Vẽ Đồ Thị

**Nhiệm vụ**: Thêm matplotlib để vẽ giá + MA

**Gợi ý**:
```python
import matplotlib.pyplot as plt

plt.plot(df['close'])
plt.plot(ma)
plt.show()
```

### Bài 4: Telegram Notifications

**Nhiệm vụ**: Gửi thông báo khi bot đặt lệnh

**Thư viện**: `python-telegram-bot`

---

## ⚠️ Phần 8: Lưu Ý An Toàn

### ❌ KHÔNG BAO GIỜ:
- Dùng API Mainnet (tiền thật) khi học
- Commit API key lên GitHub
- Trading với số tiền lớn
- Bỏ qua stop loss

### ✅ LUÔN:
- Dùng Testnet trước
- Test với số tiền nhỏ
- Backtest trước khi live
- Ghi log mọi thứ

---

## 📞 Phần 9: Hỗ Trợ

### Lỗi Thường Gặp

#### 1. "No module named 'pandas'"
```bash
pip install pandas
```

#### 2. "API key invalid"
- Kiểm tra file `.env`
- Đảm bảo copy đúng key

#### 3. "Balance insufficient"
- Nạp testnet funds vào account
- Giảm RISK_PERCENTAGE

---

## 🏆 Phần 10: Đánh Giá Dự Án

### Checklist

- [ ] Bot chạy không lỗi
- [ ] Thu thập được dữ liệu
- [ ] Tính được RSI, MA, ATR
- [ ] ChatGPT phản hồi đúng
- [ ] Đặt được lệnh (testnet)
- [ ] Log đầy đủ

### Điểm Cao Hơn

- [ ] Thêm indicator mới
- [ ] Tối ưu prompts
- [ ] Dashboard visualization
- [ ] Backtesting results
- [ ] Document đầy đủ

---

## 📚 Tài Liệu Tham Khảo

- Binance API Docs: https://binance-docs.github.io
- OpenAI API Docs: https://platform.openai.com/docs
- Python: https://www.w3schools.com/python
- Trading: https://www.investopedia.com/trading

---

**Chúc bạn thành công! 🚀**

