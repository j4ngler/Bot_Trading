"""
DEMO ĐƠN GIẢN - Không cần API Key
Dành cho học sinh muốn xem bot hoạt động mà không cần setup
"""

import random
from datetime import datetime


class SimpleDemo:
    """
    Class demo đơn giản - Mô phỏng hoạt động bot
    KHÔNG CẦN API KEY - DÙNG DỮ LIỆU GIẢ
    """
    
    def __init__(self):
        print("🎮 DEMO MODE - Không dùng API thật")
        print("=" * 60)
    
    def run_demo(self):
        """
        Chạy demo một chu kỳ
        """
        print("\n📊 CHU KỲ PHÂN TÍCH DEMO")
        print("=" * 60)
        
        # 1. Thu thập dữ liệu (GIẢ)
        print("\n1️⃣ Thu thập dữ liệu (SIMULATED)...")
        current_price = random.uniform(40000, 45000)
        print(f"   💰 Giá BTC: ${current_price:.2f}")
        
        # 2. Tính chỉ số (GIẢ)
        print("\n2️⃣ Tính chỉ số kỹ thuật...")
        ma = current_price + random.uniform(-500, 500)
        rsi = random.uniform(20, 80)
        atr = random.uniform(100, 300)
        
        print(f"   📈 MA(20): ${ma:.2f}")
        print(f"   📊 RSI(14): {rsi:.2f}")
        print(f"   📉 ATR(14): ${atr:.2f}")
        
        # Phân tích nhanh
        if rsi > 70:
            print("   ⚠️ RSI QUÁ MUA")
        elif rsi < 30:
            print("   ✅ RSI QUÁ BÁN")
        
        # 3. ChatGPT phân tích (GIẢ)
        print("\n3️⃣ ChatGPT AI phân tích...")
        if rsi > 70:
            recommendation = 'SELL'
            reason = "RSI cao cho thấy quá mua, có thể giảm sớm"
        elif rsi < 30:
            recommendation = 'BUY'
            reason = "RSI thấp cho thấy quá bán, có thể tăng"
        else:
            recommendation = 'HOLD'
            reason = "Thị trường cân bằng, đợi tín hiệu rõ ràng hơn"
        
        print(f"   🤖 Khuyến nghị: {recommendation}")
        print(f"   💬 Lý do: {reason}")
        
        # 4. Quyết định
        print("\n4️⃣ Quyết định thực thi...")
        if recommendation in ['BUY', 'SELL'] and 30 < rsi < 70:
            print("   ✅ Điều kiện đạt - Sẽ đặt lệnh")
            print(f"   📊 Số lượng: {random.uniform(0.001, 0.01):.6f} BTC")
            print("   💰 Chi phí: $50 (demo)")
        else:
            print("   ⏸️ Giữ nguyên - Không giao dịch")
        
        print("\n" + "=" * 60)
        print("✅ Hoàn thành chu kỳ DEMO")


def main():
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║        DEMO TRADING BOT - KHÔNG CẦN API KEY           ║
    ║            Mô phỏng hoạt động bot đơn giản             ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    demo = SimpleDemo()
    
    # Chạy 3 chu kỳ demo
    for i in range(3):
        print(f"\n🔄 Chu kỳ {i+1}/3")
        demo.run_demo()
    
    print("\n" + "=" * 60)
    print("🎉 DEMO hoàn thành!")
    print("\n💡 Để chạy bot thật:")
    print("   1. Setup API keys (Binance Testnet + OpenAI)")
    print("   2. Chạy: python main.py")
    print("   3. Xem hướng dẫn: HUONG_DAN_HOC_SINH.md")


if __name__ == '__main__':
    main()

