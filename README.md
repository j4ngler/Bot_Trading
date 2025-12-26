# 🤖 Trading Bot - Trợ Lý Ảo Giao Dịch Tự Động

> **Hệ thống giao dịch tự động sử dụng ChatGPT AI + Binance Testnet**  
> Phù hợp cho học sinh cấp 3 - Học về AI, API, và Trading

---

## 📋 Tổng Quan

### Mục Tiêu Dự Án

Xây dựng một **trading bot tự động** có khả năng:

- ✅ Thu thập dữ liệu thị trường từ Binance **Testnet** (an toàn)
- ✅ Tính toán **chỉ báo kỹ thuật** (MA, RSI, ATR)
- ✅ Sử dụng **ChatGPT AI** để phân tích và đưa ra khuyến nghị
- ✅ Tự động **thực thi lệnh** (Mua/Bán) dựa trên AI
- ✅ **Logging & báo cáo** hiệu suất giao dịch

---

## 🧩 Kiến Trúc Hệ Thống

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Data Collector │────>│ Tech Indicators │────>│ ChatGPT Advisor │
│  (Binance API)  │     │  (MA, RSI, ATR) │     │  (AI Analysis)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
      ↓                        ↓                        ↓
      └──────────┬─────────────┴───────────────────────┘
                 ↓
       ┌─────────────────────┐
       │ Risk & Order Mgr    │ ← Tính volume, StopLoss/TakeProfit
       └─────────────────────┘
                 ↓
       ┌─────────────────────┐
       │ Trade Executor      │ → Gửi lệnh giao dịch
       └─────────────────────┘
                 ↓
       ┌─────────────────────┐
       │ Database & Logger   │ → Lưu lịch sử, dữ liệu, kết quả
       └─────────────────────┘
                 ↓
       ┌─────────────────────┐
       │ Reporting & Monitor │ → Báo cáo, biểu đồ vốn
       └─────────────────────┘
```

### Luồng Hoạt Động

1. **Thu thập dữ liệu** → Lấy giá BTC/USDT từ Binance
2. **Tính chỉ số** → MA, RSI, ATR
3. **AI phân tích** → ChatGPT đưa ra khuyến nghị BUY/SELL/HOLD
4. **Kiểm tra rủi ro** → Risk Manager xác định có an toàn giao dịch
5. **Tính vị thế** → Tính khối lượng, stop loss, take profit
6. **Thực thi** → Gửi lệnh (nếu hợp lý)
7. **Log** → Lưu vào database
8. **Báo cáo** → Tổng hợp hiệu suất và vẽ biểu đồ

---

## ⚙️ Cài Đặt

### Yêu Cầu

- Python 3.8+
- Tài khoản OpenAI API
- Tài khoản Binance Testnet

### Bước 1: Clone Project

```bash
cd TradingBot
```

### Bước 2: Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

### Bước 3: Cấu Hình API Keys

1. Copy file `.env.example` thành `.env`
2. Điền API keys:

```bash
# Binance Testnet
BINANCE_API_KEY=your_testnet_key
BINANCE_SECRET_KEY=your_testnet_secret

# OpenAI
OPENAI_API_KEY=sk-your_key
```

#### Lấy Binance Testnet API:
1. Truy cập: https://testnet.binance.vision/
2. Đăng ký/đăng nhập
3. Vào "API Management" → Tạo API key mới
4. Copy key và secret

#### Lấy OpenAI API:
1. Truy cập: https://platform.openai.com
2. Vào "API keys" → Tạo key mới
3. Copy key (bắt đầu bằng `sk-`)

---

## 🚀 Sử Dụng

### Chạy Bot (GUI mặc định)

```bash
python run.py
```

- Lệnh trên tự động mở giao diện TradingBotGUI với đầy đủ tab Logs/Báo cáo/Chat.

### Example: compute MACD + Fibonacci signals

You can compute MACD and Fibonacci-based signals locally using the helper module `src/strategy_signals.py`.

Example (from repository root):

```bash
python -c "from src.strategy_signals import generate_signals; import pandas as pd; df = pd.read_csv('data/sample_prices.csv'); print(generate_signals(df))"
```

This will print a conservative recommendation (BUY/SELL/HOLD) plus entry/stop suggestions derived from MACD crosses and Fibonacci retracement levels.

- Use this helper for quick local testing and visualization before wiring signals into `src/main.py` or `src/chatgpt_advisor.py`.
- Trong trường hợp môi trường không hỗ trợ GUI, chương trình tự chuyển sang chế độ CLI liên tục (thông báo ngay trong terminal).

### Chế Độ GUI (main.py - Mặc định)

Khi chạy `python main.py`, GUI sẽ tự động mở:
- **Giao diện đồ họa** với các nút điều khiển
- **Tab Logs**: Xem log hoạt động của bot
- **Tab Báo Cáo**: Xem báo cáo hiệu suất và biểu đồ trực tiếp
- **Tự động cập nhật** mỗi 5 phút sau khi nhấn "BẮT ĐẦU"

---

## 📂 Cấu Trúc Project

```
TradingBot/
├── run.py                     # 🚀 Entry point chính (GUI mode)
├── requirements.txt           # Dependencies
├── .env                       # API keys (tự tạo)
├── README.md                  # File này
│
├── src/                       # 📦 Source code chính
│   ├── __init__.py
│   ├── main.py                # Bot chính (gọi GUI, fallback CLI)
│   ├── app.py                 # Vòng lặp auto + chat CLI (dùng nội bộ/backup)
│   ├── gui_app.py             # ✨ Module GUI với Tkinter
│   ├── config.py               # Cấu hình
│   ├── data_collector.py       # Thu thập dữ liệu Binance
│   ├── technical_indicators.py # Tính chỉ báo kỹ thuật (MA, RSI, ATR)
│   ├── chatgpt_advisor.py      # AI advisor phân tích thị trường
│   ├── trade_executor.py       # Thực thi lệnh giao dịch
│   ├── risk_manager.py         # ✨ Quản lý rủi ro & vị thế
│   ├── database_logger.py      # ✨ Database & logging
│   └── reporting_monitoring.py  # ✨ Báo cáo & giám sát
│
├── data/                      # 📊 Dữ liệu và output
│   ├── trading_history.db     # Database lịch sử giao dịch
│   ├── trading_logs.txt        # Log file
│   ├── trading_report.html     # Báo cáo HTML
│   └── duong_cong_von.png      # Biểu đồ vốn
│
├── docs/                      # 📚 Tài liệu
│   ├── WORKFLOW.md
│   ├── CHANGELOG.md
│   ├── HUONG_DAN_HOC_SINH.md
│   ├── Giao_An_TradingBot.tex
│   ├── Trading_Bot_Ly_Thuyet.tex
│   └── ... (PDF, DOCX, PPTX)
│
└── scripts/                   # 🔧 Utility scripts
    ├── compile_latex.py
    └── demo_simple.py
```

---

## 🎓 Học Gì?

- **Python**: APIs, modules, classes
- **Trading**: MA, RSI, ATR, market orders
- **AI**: OpenAI GPT, prompts

---

## 📊 Khái Niệm Chỉ Báo Kỹ Thuật (RSI, MA, ATR)

### 1. RSI (Relative Strength Index) - Chỉ Số Sức Mạnh Tương Đối

**Định nghĩa:**
- RSI là chỉ báo đo tốc độ và quy mô biến động giá gần đây
- Giá trị từ 0 đến 100
- Được phát triển bởi J. Welles Wilder (1978)

**Công thức:**
```
RSI = 100 - (100 / (1 + RS))
Trong đó: RS = Trung bình tăng / Trung bình giảm (trong 14 phiên)
```

**Ý nghĩa:**
- **RSI > 70**: Thị trường **QUÁ MUA** (Overbought)
  - Nhiều người đã mua → Cầu giảm → Giá có thể điều chỉnh xuống
  - ⚠️ **Bot không mua** khi RSI > 70
  
- **RSI < 30**: Thị trường **QUÁ BÁN** (Oversold)
  - Nhiều người đã bán → Cung giảm → Giá có thể phục hồi
  - ✅ **Bot cân nhắc mua** khi RSI < 30
  
- **RSI 30-70**: Thị trường **CÂN BẰNG**
  - Không có tín hiệu rõ ràng → Bot thường HOLD

**Ví dụ thực tế:**
```
Giá BTC: $43,250
RSI: 72.5
→ RSI > 70 → QUÁ MUA
→ Bot khuyến nghị: SELL hoặc HOLD
→ Không nên mua vào lúc này
```

---

### 2. MA (Moving Average) - Đường Trung Bình Động

**Định nghĩa:**
- MA là giá trung bình của một tài sản trong N phiên gần nhất
- Làm mịn biến động giá, giúp nhận diện xu hướng

**Các loại MA:**
- **SMA (Simple Moving Average)**: Trung bình số học đơn giản
  ```
  SMA(20) = (Giá1 + Giá2 + ... + Giá20) / 20
  ```
  
- **EMA (Exponential Moving Average)**: Trung bình hàm mũ
  - Ưu tiên dữ liệu gần đây hơn
  - Phản ứng nhanh hơn với biến động mới

**Ý nghĩa:**
- **Giá > MA**: Xu hướng **TĂNG** (Bullish)
  - Giá đang ở trên mức trung bình → Lực mua mạnh
  - ✅ Bot có thể cân nhắc BUY
  
- **Giá < MA**: Xu hướng **GIẢM** (Bearish)
  - Giá đang ở dưới mức trung bình → Lực bán mạnh
  - ⚠️ Bot có thể cân nhắc SELL
  
- **MA ngắn cắt lên MA dài**: Tín hiệu **MUA** (Golden Cross)
- **MA ngắn cắt xuống MA dài**: Tín hiệu **BÁN** (Death Cross)

**Ví dụ thực tế:**
```
Giá BTC: $43,250
MA(20): $42,800
→ Giá > MA → Xu hướng TĂNG
→ Bot phân tích: Thị trường đang tích cực
```

**Trong bot:**
- Bot dùng **MA(20)** - trung bình 20 phiên
- So sánh giá hiện tại với MA để xác định xu hướng

---

### 3. ATR (Average True Range) - Biên Độ Dao Động Trung Bình

**Định nghĩa:**
- ATR đo lường **mức độ biến động** (volatility) của giá
- Được phát triển bởi J. Welles Wilder (1978)
- Giá trị càng cao → Thị trường càng biến động

**Công thức:**
```
True Range (TR) = Max của:
  - High - Low (biên độ trong phiên)
  - |High - Close trước| (gap tăng)
  - |Low - Close trước| (gap giảm)

ATR = Trung bình của TR trong 14 phiên
```

**Ý nghĩa:**
- **ATR cao**: Thị trường **biến động mạnh**
  - Giá nhảy mạnh → Cần đặt **Stop Loss xa hơn**
  - Rủi ro cao → Bot cẩn thận hơn
  
- **ATR thấp**: Thị trường **ổn định**
  - Giá ít biến động → Có thể đặt **Stop Loss gần hơn**
  - Rủi ro thấp → Bot có thể giao dịch an toàn hơn

**Ứng dụng trong bot:**
- **Đặt Stop Loss động:**
  ```
  Nếu có ATR:
    Stop Loss = Entry Price - (2 × ATR)  [cho lệnh BUY]
    Take Profit = Entry Price + (3 × ATR)
  
  Nếu không có ATR:
    Stop Loss = Entry Price × (1 - 2%)  [cố định 2%]
    Take Profit = Entry Price × (1 + 3%)  [cố định 3%]
  ```

**Ví dụ thực tế:**
```
Giá BTC: $43,250
ATR: $250
→ ATR = $250 → Biến động trung bình

Stop Loss (dùng ATR):
  = $43,250 - (2 × $250)
  = $42,750  [Cách entry 1.16%]

Stop Loss (cố định 2%):
  = $43,250 × 0.98
  = $42,385  [Cách entry 2%]

→ Dùng ATR linh hoạt hơn, phù hợp với biến động thực tế
```

**Trong bot:**
- Bot tính **ATR(14)** - biên độ trung bình 14 phiên
- Dùng ATR để điều chỉnh Stop Loss/Take Profit tự động
- Nếu ATR quá cao (>5% giá) → Bot **không giao dịch** (quá rủi ro)

---

### 4. Tổng Hợp: Cách Bot Sử Dụng 3 Chỉ Báo

| Chỉ Báo | Mục Đích | Bot Sử Dụng |
|---------|----------|-------------|
| **RSI** | Phát hiện quá mua/quá bán | Chặn giao dịch khi RSI > 70 hoặc < 30 |
| **MA** | Xác định xu hướng | So sánh giá với MA để quyết định BUY/SELL |
| **ATR** | Đo biến động | Điều chỉnh Stop Loss/Take Profit linh hoạt |

**Ví dụ kết hợp:**
```
Giá: $43,250
MA(20): $42,800  → Giá > MA (xu hướng tăng)
RSI: 65          → Cân bằng (30-70)
ATR: $250        → Biến động bình thường

→ Bot phân tích:
  ✅ Xu hướng tăng (giá > MA)
  ✅ RSI an toàn (không quá cực)
  ✅ ATR ổn định
  
→ ChatGPT có thể khuyến nghị: BUY
→ Risk Manager kiểm tra: Pass
→ Bot thực thi lệnh với Stop Loss = 2×ATR
```

---

## 🧠 Lý Thuyết Kinh Tế – Tài Chính Nền Tảng (gắn với Trading Bot)

### 1) Kinh tế học vi mô: Cung – Cầu và Kỳ vọng
- **Cung – Cầu**: Giá tăng khi cầu > cung; giảm khi cung > cầu. Trong crypto, kỳ vọng tương lai làm cầu thay đổi rất nhanh.
- **Ứng dụng trong bot**:
  - `RSI > 70` hiểu như trạng thái “đã có quá nhiều người mua” → cầu suy yếu → rủi ro đảo chiều tăng.
  - `RSI < 30` hiểu như “đã có quá nhiều người bán” → áp lực cung suy yếu → dễ phục hồi.
- **Kỳ vọng & EMH (Efficient Market Hypothesis)**: Bot phản ứng theo dữ liệu gần nhất (RSI/MA/ATR) tương ứng giả định thị trường hiệu quả mức “yếu” (giá phản ánh dữ liệu quá khứ), nên vẫn còn chỗ cho chiến lược phản ứng nhanh.

### 2) Kinh tế học hành vi: Vì sao cần kỷ luật máy móc

**Tại sao con người thường thua lỗ trong trading?** Nghiên cứu cho thấy 90% trader thua lỗ không phải vì thiếu kiến thức, mà vì **cảm xúc chi phối quyết định**. Bot tự động loại bỏ yếu tố này.

#### 📉 Loss Aversion (Ghét thua lỗ - Thiên kiến mất mát)

**Định nghĩa:** Con người cảm nhận nỗi đau mất $100 mạnh gấp 2-2.5 lần niềm vui khi kiếm được $100. Điều này khiến trader:
- Giữ lệnh lỗ quá lâu, hy vọng giá quay lại
- Cắt lời quá sớm vì sợ mất lợi nhuận đã có
- Không dám vào lệnh mới sau khi thua

**Ví dụ thực tế:**
```
Trader mua BTC ở $40,000
Giá giảm xuống $38,000 (lỗ $2,000)
→ "Chờ giá quay lại, không bán lỗ!"
→ Giá tiếp tục giảm xuống $35,000 (lỗ $5,000)
→ Vẫn không bán vì "đã lỗ rồi, chờ thêm"
→ Cuối cùng giá xuống $30,000 → Mất $10,000
```

**Bot xử lý như thế nào:**
- Bot đặt **Stop Loss cứng** ngay khi vào lệnh (không có cảm xúc)
- Trong `risk_manager.py`, Stop Loss được tính tự động:
  ```python
  # Nếu có ATR: SL = Entry - (2 × ATR)
  # Nếu không: SL = Entry × (1 - 2%)
  ```
- Khi giá chạm Stop Loss → Bot tự động bán, không do dự
- **Kết quả:** Chỉ mất tối đa 1% vốn/lệnh, không bao giờ "thổi bay" tài khoản

#### 🚨 FOMO (Fear Of Missing Out - Sợ bỏ lỡ)

**Định nghĩa:** Khi thấy giá tăng mạnh, trader sợ bỏ lỡ cơ hội → mua đuổi ở đỉnh, thường là lúc giá sắp đảo chiều.

**Ví dụ thực tế:**
```
BTC đang ở $40,000
→ Giá tăng lên $42,000 (tin tức tốt)
→ Trader: "Mình đã bỏ lỡ! Phải mua ngay!"
→ Mua ở $42,000
→ Giá đảo chiều, giảm xuống $38,000
→ Lỗ $4,000 ngay lập tức
```

**Bot xử lý như thế nào:**
- Bot kiểm tra điều kiện trong `risk_manager.check_risk_conditions()`:
  ```python
  # Chặn giao dịch nếu RSI > 75 (quá mua)
  if rsi > 75:
      return False, "RSI quá cao - Thị trường quá mua"
  
  # Chặn nếu biến động quá cao
  if atr / current_price > 0.05:  # ATR > 5% giá
      return False, "Biến động quá cao"
  ```
- Khi RSI > 70 hoặc ATR/giá > 5% → Bot **tự động từ chối** giao dịch
- **Kết quả:** Bot không bao giờ mua đuổi ở đỉnh, tránh được FOMO

#### 🐑 Herding (Bầy đàn - Tâm lý đám đông)

**Định nghĩa:** Con người có xu hướng làm theo đám đông. Khi nhiều người mua → giá tăng → nhiều người mua hơn → tạo bong bóng. Khi nhiều người bán → giá giảm → nhiều người bán hơn → tạo hoảng loạn.

**Ví dụ thực tế:**
```
Thị trường đang "hưng phấn":
- RSI = 78 (quá mua)
- Giá tăng 10% trong 1 ngày
- Mọi người đều mua → FOMO lan truyền
→ Đây là lúc nguy hiểm nhất, giá sắp đảo chiều
```

**Bot xử lý như thế nào:**
- Bot nhận diện "bầy đàn" qua:
  - **RSI cực cao** (>75) → Nhiều người đã mua
  - **Biến động cao** (ATR/giá > 5%) → Thị trường không ổn định
- Bot **không giao dịch** khi phát hiện tín hiệu này
- **Kết quả:** Bot tránh được "bẫy đám đông", giao dịch ngược lại khi thị trường quá cực

#### ⚓ Anchoring (Neo giá mua - Thiên kiến neo)

**Định nghĩa:** Trader "neo" vào giá mua ban đầu, không chịu thay đổi quyết định dựa trên dữ liệu mới.

**Ví dụ thực tế:**
```
Trader mua BTC ở $40,000
→ Giá giảm xuống $35,000
→ Trader: "Mình mua ở $40k, phải đợi giá về $40k mới bán"
→ Bỏ qua tín hiệu bán từ chỉ báo kỹ thuật
→ Giá tiếp tục giảm → Lỗ lớn
```

**Bot xử lý như thế nào:**
- Bot **không nhớ** giá mua cũ
- Mỗi chu kỳ, bot phân tích lại từ đầu dựa trên:
  - Giá hiện tại
  - Chỉ báo kỹ thuật mới nhất (MA, RSI, ATR)
  - Khuyến nghị ChatGPT mới nhất
- Bot ra quyết định **hoàn toàn dựa trên dữ liệu hiện tại**, không bị ảnh hưởng bởi lịch sử
- **Kết quả:** Bot linh hoạt, thích ứng nhanh với thị trường

---

### 3) Lý thuyết danh mục & rủi ro: Vì sao chỉ mạo hiểm 1% vốn/lệnh

#### 💰 Quy tắc 1% - Bảo vệ tài khoản

**Tại sao 1%?** Nếu bạn mạo hiểm quá nhiều mỗi lệnh, chỉ cần 10-20 lệnh lỗ liên tiếp là tài khoản sẽ "thổi bay".

**Ví dụ so sánh:**

| Rủi ro/lệnh | Số lệnh lỗ để mất 50% vốn | Số lệnh lỗ để mất 100% vốn |
|-------------|---------------------------|----------------------------|
| **1%** (Bot dùng) | 69 lệnh | 100 lệnh |
| 5% | 14 lệnh | 20 lệnh |
| 10% | 7 lệnh | 10 lệnh |
| 20% | 3 lệnh | 5 lệnh |

**Kết luận:** Với 1% rủi ro, bạn có thể chịu được **100 lệnh lỗ liên tiếp** trước khi mất hết vốn. Điều này gần như không thể xảy ra nếu bot hoạt động đúng.

**Trong bot:**
```python
# risk_manager.py - Dòng 60
risk_amount = self.account_balance * (self.risk_percent / 100)  # 1% vốn
```

#### 📊 Position Sizing (Tính khối lượng vị thế)

**Công thức:**
```
Khối lượng = (Vốn × Risk%) / (Giá × StopLoss%)
```

**Ví dụ cụ thể:**
```
Vốn: $10,000
Risk: 1% = $100
Giá BTC: $43,250
Stop Loss: 2% = $865 (khoảng cách từ entry)

Khối lượng = $100 / $865 = 0.1156 BTC
Giá trị lệnh = 0.1156 × $43,250 = $5,000
```

**Tại sao công thức này?**
- Nếu giá giảm 2% (chạm Stop Loss) → Bạn chỉ mất đúng $100 (1% vốn)
- Không phụ thuộc vào giá BTC → Luôn rủi ro 1% dù BTC ở $30k hay $60k

**Trong bot:**
```python
# risk_manager.py - Dòng 38-100
def calculate_position_size(self, entry_price, signal, current_atr=None):
    risk_amount = self.account_balance * (self.risk_percent / 100)  # $100
    stop_loss_amount = entry_price * (self.stop_loss_percent / 100)  # $865
    quantity = risk_amount / stop_loss_amount  # 0.1156 BTC
    return {'quantity': quantity, 'risk_amount': risk_amount, ...}
```

#### ⚖️ Risk/Reward Ratio (Tỷ lệ Rủi ro/Lợi nhuận)

**Định nghĩa:** Tỷ lệ giữa lợi nhuận kỳ vọng và rủi ro tối đa.

**Công thức:**
```
R/R = (Take Profit - Entry) / (Entry - Stop Loss)
```

**Ví dụ:**
```
Entry: $43,250
Stop Loss: $42,385 (giảm 2%)
Take Profit: $44,548 (tăng 3%)

R/R = ($44,548 - $43,250) / ($43,250 - $42,385)
    = $1,298 / $865
    = 1.5
```

**Ý nghĩa:**
- R/R = 1.5 → Nếu thắng, bạn kiếm $1.5 cho mỗi $1 rủi ro
- Nếu tỷ lệ thắng 50%, bạn vẫn có lời về lâu dài
- **Quy tắc:** Chỉ vào lệnh nếu R/R ≥ 1.5

**Trong bot:**
```python
# risk_manager.py - Dòng 150-175
def calculate_risk_reward_ratio(self, entry, stop_loss, take_profit):
    risk = abs(entry - stop_loss)
    reward = abs(take_profit - entry)
    ratio = reward / risk if risk > 0 else 0
    return round(ratio, 2)  # Trả về 1.5
```

#### 🎯 Kelly Criterion (Tiêu chí Kelly - Nâng cao)

**Định nghĩa:** Công thức toán học tính tỷ lệ vốn tối ưu dựa trên xác suất thắng và R/R ratio.

**Công thức:**
```
Kelly % = (Win Rate × R/R - Loss Rate) / R/R
```

**Ví dụ:**
```
Win Rate: 60% (thắng 6/10 lệnh)
Loss Rate: 40% (thua 4/10 lệnh)
R/R: 1.5

Kelly % = (0.6 × 1.5 - 0.4) / 1.5
        = (0.9 - 0.4) / 1.5
        = 0.5 / 1.5
        = 33.3%
```

**Lưu ý:** Kelly Criterion thường quá mạo hiểm. Bot dùng **"Half Kelly"** (50% của Kelly) hoặc **1% cố định** để an toàn hơn.

---

### 4) Volatility (ATR) và kịch bản dừng lỗ/chốt lời

#### 📈 ATR (Average True Range) - Đo biến động

**Tại sao cần ATR?** Thị trường không phải lúc nào cũng biến động như nhau. Có ngày giá nhảy $500, có ngày chỉ nhảy $50. Stop Loss cố định 2% không phù hợp với mọi tình huống.

**Ví dụ so sánh:**

| Tình huống | Giá BTC | ATR | Biến động | Stop Loss cố định 2% | Stop Loss dùng ATR |
|------------|---------|-----|-----------|---------------------|-------------------|
| Thị trường ổn định | $43,250 | $100 | Thấp | $865 (2%) | $200 (2×ATR = 0.46%) |
| Thị trường biến động | $43,250 | $500 | Cao | $865 (2%) | $1,000 (2×ATR = 2.3%) |

**Kết luận:**
- Khi ATR thấp → Stop Loss gần hơn → Bảo vệ tốt hơn
- Khi ATR cao → Stop Loss xa hơn → Tránh bị "stop out" bởi noise

**Trong bot:**
```python
# risk_manager.py - Dòng 69-74
if current_atr and current_atr > 0:
    # Dùng 2x ATR làm stop loss (linh hoạt)
    atr_stop_loss = current_atr * 2
    stop_loss_price = entry_price - atr_stop_loss  # Cho lệnh BUY
    take_profit_price = entry_price + (current_atr * 3)  # 3×ATR cho TP
else:
    # Dùng % cố định nếu không có ATR
    stop_loss_price = entry_price * (1 - 2%)
```

**Ví dụ cụ thể:**
```
Entry: $43,250
ATR: $250

Stop Loss (dùng ATR): $43,250 - (2 × $250) = $42,750
Take Profit (dùng ATR): $43,250 + (3 × $250) = $44,000

R/R = ($44,000 - $43,250) / ($43,250 - $42,750)
    = $750 / $500
    = 1.5 ✅ (Hợp lý)
```

---

### 5) Chu kỳ thị trường và tâm lý số đông

#### 🔄 Chu kỳ tâm lý thị trường

Thị trường crypto trải qua các giai đoạn tâm lý lặp đi lặp lại:

```
1. Tích luỹ (Accumulation)
   → RSI thấp (20-30), giá ổn định
   → Ít người quan tâm
   → Bot: Có thể mua (cơ hội tốt)

2. Hoài nghi (Disbelief)
   → Giá bắt đầu tăng nhẹ
   → Nhiều người vẫn hoài nghi
   → Bot: Theo dõi, chờ tín hiệu rõ ràng

3. Lạc quan (Optimism)
   → Giá tăng mạnh
   → RSI tăng (50-70)
   → Bot: Có thể mua (xu hướng tăng)

4. Hưng phấn (Euphoria) ⚠️
   → RSI rất cao (>75)
   → Giá tăng mạnh, mọi người FOMO
   → Bot: KHÔNG GIAO DỊCH (quá nguy hiểm)

5. Hoảng loạn (Panic)
   → Giá giảm mạnh
   → RSI rất thấp (<25)
   → Bot: Cân nhắc mua (cơ hội hồi phục)

6. Trầm cảm (Depression)
   → Giá tiếp tục giảm
   → Nhiều người bán tháo
   → Bot: Chờ tín hiệu tích luỹ
```

**Bot nhận diện chu kỳ như thế nào:**

```python
# risk_manager.py - Dòng 119-123
if rsi > 75:
    return False, "RSI quá cao (>75) - Thị trường quá mua (Hưng phấn)"
elif rsi < 25:
    return False, "RSI quá thấp (<25) - Thị trường quá bán (Hoảng loạn)"
```

**Ví dụ thực tế:**
```
Tình huống: BTC tăng từ $40k → $50k trong 1 tuần
RSI: 78 (quá mua)
ATR: $800 (biến động cao)
→ Bot nhận diện: "Hưng phấn" - Giai đoạn nguy hiểm
→ Bot: KHÔNG GIAO DỊCH
→ Kết quả: Giá đảo chiều, giảm về $42k
→ Bot tránh được lỗ lớn
```

---

### 6) Bảng quy chiếu nhanh: Lý thuyết → Thực thi trong bot

| Lý thuyết | Ứng dụng trong bot | File code | Ví dụ |
|-----------|-------------------|-----------|-------|
| **Cung–Cầu** | Dùng RSI/MA để suy luận áp lực mua bán | `technical_indicators.py` | RSI > 70 → Cầu yếu → Không mua |
| **Loss Aversion** | Stop Loss cứng, tự động cắt lỗ | `risk_manager.py` (dòng 69-82) | SL = Entry - 2×ATR |
| **FOMO** | Chặn giao dịch khi RSI > 75 hoặc ATR/giá > 5% | `risk_manager.py` (dòng 119-134) | RSI = 78 → Không giao dịch |
| **Herding** | Nhận diện cực trị qua RSI + ATR | `risk_manager.py` (dòng 130-134) | RSI cao + ATR cao → Bỏ qua |
| **Anchoring** | Mỗi chu kỳ phân tích lại từ đầu | `main.py` (dòng 65-157) | Không nhớ giá cũ |
| **Quy tắc 1%** | Risk 1%/lệnh, tính khối lượng theo SL | `risk_manager.py` (dòng 60-66) | $10k vốn → $100 rủi ro/lệnh |
| **Position Sizing** | Công thức: `(Vốn × 1%) / (Giá × SL%)` | `risk_manager.py` (dòng 38-100) | Quantity = $100 / $865 |
| **Risk/Reward** | Tính R/R ratio, chỉ vào lệnh nếu ≥ 1.5 | `risk_manager.py` (dòng 150-175) | R/R = 1.5 → OK |
| **Volatility (ATR)** | Điều chỉnh SL/TP linh hoạt theo ATR | `risk_manager.py` (dòng 69-74) | SL = 2×ATR, TP = 3×ATR |
| **Chu kỳ tâm lý** | Nhận diện vùng cực trị (RSI > 75 hoặc < 25) | `risk_manager.py` (dòng 119-123) | RSI = 78 → "Hưng phấn" → Không giao dịch |

---

## 💡 Ví Dụ Output

```
📊 Giá: $43,250 | MA: $42,800 | RSI: 72.5 | ATR: $250
🤖 ChatGPT: SELL (RSI cao, quá mua)
⏸️ KHÔNG thực thi - RSI quá cực, không an toàn
```

---

## ⚠️ Lưu Ý Quan Trọng

1. **CHỈ DÙNG BINANCE TESTNET** - Không dùng tiền thật
2. **API có chi phí** - OpenAI charge theo token
3. **Không phải lời khuyên đầu tư** - Chỉ học tập
4. **Rủi ro cao** - Trading có thể mất tiền
5. **Backup code** - Commit thường xuyên

---

## 🎯 Tính Năng

✅ Binance Testnet integration  
✅ Tính chỉ báo kỹ thuật (MA, RSI, ATR)  
✅ ChatGPT AI phân tích thị trường  
✅ Quản lý rủi ro tự động (Risk Manager)  
✅ Database & logging chi tiết  
✅ Báo cáo hiệu suất & biểu đồ vốn  
✅ Auto trading với stop loss/take profit

📖 Xem hướng dẫn chi tiết: `HUONG_DAN_HOC_SINH.md`

---

## 🐛 Lỗi Thường Gặp

| Lỗi | Giải pháp |
|-----|-----------|
| API key invalid | Kiểm tra file `.env` |
| OpenAI limit | Giảm frequency hoặc check billing |
| Balance insufficient | Nạp testnet funds |

---

**📖 Đọc thêm**: `HUONG_DAN_HOC_SINH.md` để biết chi tiết

**⚠️ Educational Use Only - Không dùng tiền thật!**

