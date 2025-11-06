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

### Chạy Bot

```bash
python main.py
```

### Các Chế Độ

Sau khi chạy `python main.py`, bạn sẽ thấy menu chọn:
- **0️⃣ Chạy với GIAO DIỆN GUI (Tkinter)** - Giao diện đồ họa với các nút điều khiển
- **1️⃣ Chạy MỘT LẦN** - Phân tích và dừng
- **2️⃣ Chạy LIÊN TỤC** - Tự động mỗi 15 phút  
- **3️⃣ Chạy DEMO** - Chỉ phân tích, không giao dịch
- **4️⃣ Xem BÁO CÁO** - Hiệu suất giao dịch (HTML + biểu đồ)

---

## 📂 Cấu Trúc Project

```
TradingBot/
├── main.py                    # File chính - Entry point (Menu chọn GUI/CLI)
├── gui_app.py                 # ✨ Module GUI với Tkinter
├── config.py                  # Cấu hình
├── data_collector.py          # Thu thập dữ liệu Binance
├── technical_indicators.py    # Tính chỉ báo kỹ thuật (MA, RSI, ATR)
├── chatgpt_advisor.py         # AI advisor phân tích thị trường
├── trade_executor.py          # Thực thi lệnh giao dịch
├── risk_manager.py            # ✨ MỚI: Quản lý rủi ro & vị thế
├── database_logger.py         # ✨ MỚI: Database & logging
├── reporting_monitoring.py    # ✨ MỚI: Báo cáo & giám sát
├── requirements.txt           # Dependencies
├── .env                       # API keys (tự tạo)
└── README.md                  # File này
```

---

## 🎓 Học Gì?

- **Python**: APIs, modules, classes
- **Trading**: MA, RSI, ATR, market orders
- **AI**: OpenAI GPT, prompts

---

## 🧠 Lý Thuyết Kinh Tế – Tài Chính Nền Tảng (gắn với Trading Bot)

### 1) Kinh tế học vi mô: Cung – Cầu và Kỳ vọng
- **Cung – Cầu**: Giá tăng khi cầu > cung; giảm khi cung > cầu. Trong crypto, kỳ vọng tương lai làm cầu thay đổi rất nhanh.
- **Ứng dụng trong bot**:
  - `RSI > 70` hiểu như trạng thái “đã có quá nhiều người mua” → cầu suy yếu → rủi ro đảo chiều tăng.
  - `RSI < 30` hiểu như “đã có quá nhiều người bán” → áp lực cung suy yếu → dễ phục hồi.
- **Kỳ vọng & EMH (Efficient Market Hypothesis)**: Bot phản ứng theo dữ liệu gần nhất (RSI/MA/ATR) tương ứng giả định thị trường hiệu quả mức “yếu” (giá phản ánh dữ liệu quá khứ), nên vẫn còn chỗ cho chiến lược phản ứng nhanh.

### 2) Kinh tế học hành vi: Vì sao cần kỷ luật máy móc
- **Loss Aversion (ghét thua lỗ)**: Con người giữ lệnh lỗ quá lâu; bot đặt `Stop Loss` cứng để loại cảm xúc.
- **FOMO**: Sợ bỏ lỡ khiến mua đuổi ở đỉnh; bot chặn bằng điều kiện `RSI > 70` hoặc `ATR/giá > ngưỡng` → “thị trường quá nóng, bỏ qua”.
- **Herding (bầy đàn)**: Dòng tiền theo đám đông tạo cực trị; bot nhận diện qua RSI/biến động cao để tránh giao dịch ngược lợi ích.
- **Anchoring (neo giá mua)**: Con người bám vào “giá vốn”; bot luôn ra quyết định dựa trên dữ liệu mới nhất.

### 3) Lý thuyết danh mục & rủi ro: Vì sao chỉ mạo hiểm 1% vốn/lệnh
- **Quy tắc 1%**: Tối đa rủi ro mỗi lệnh = 1% tổng vốn → khó bị “thổi bay” tài khoản.
- **Position Sizing**: `Khối lượng = (Vốn × Risk%) / (Giá × StopLoss%)` → gắn trực tiếp với `risk_manager.py`.
- **Risk/Reward (R/R)**: Chỉ vào lệnh nếu tỷ lệ lợi nhuận kỳ vọng so với rủi ro đủ tốt (ví dụ ≥ 1.5).
- **Kelly Criterion (tuỳ chọn nâng cao)**: Ước lượng tỉ lệ vốn tối ưu theo xác suất thắng – nên dùng phiên bản thận trọng (nửa Kelly) để giảm biến động.

### 4) Volatility (ATR) và kịch bản dừng lỗ/chốt lời
- **ATR** đo biên độ dao động: biến động cao → cần `Stop Loss` rộng hơn; biến động thấp → `SL` hẹp hơn.
- **Trong bot**: nếu có ATR, `SL ≈ 2×ATR`, `TP ≈ 3×ATR` (logic trong `risk_manager.py`).

### 5) Chu kỳ thị trường và tâm lý số đông
- Các pha phổ biến: Hoài nghi → Lạc quan → Hưng phấn → Hoảng loạn → Trầm cảm → Tích luỹ.
- **Trong bot**: RSI rất cao kèm biến động mạnh thường rơi vào vùng “hưng phấn” → ưu tiên phòng thủ; RSI rất thấp có thể là “hoảng loạn” → cân nhắc cơ hội hồi phục (nhưng vẫn tuân thủ SL).

### 6) Bảng quy chiếu nhanh: Lý thuyết → Thực thi trong bot
- **Cung–Cầu** → Dùng RSI/MA để suy luận áp lực mua bán ngắn hạn.
- **Hành vi (Loss Aversion/FOMO)** → Kỷ luật SL cố định, chặn giao dịch khi thị trường quá nóng.
- **Danh mục & Rủi ro** → Risk 1%/lệnh, tính khối lượng theo StopLoss.
- **Volatility** → ATR điều chỉnh SL/TP linh hoạt.
- **Chu kỳ tâm lý** → Nhận diện vùng cực trị để giảm rủi ro vào lệnh.

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

