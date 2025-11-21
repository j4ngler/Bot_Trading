"""
Module tính toán các chỉ báo kỹ thuật (Technical Indicators)
Phù hợp cho học sinh cấp 3 - giải thích rõ ràng từng chỉ số
"""

import pandas as pd
import pandas_ta as ta  # Thư viện tính indicators


class TechnicalIndicators:
    """
    Class tính toán các chỉ báo kỹ thuật
    - MA: Moving Average (Đường trung bình động)
    - RSI: Relative Strength Index (Chỉ số sức mạnh tương đối)
    - ATR: Average True Range (Biên độ dao động trung bình)
    """
    
    @staticmethod
    def calculate_ma(df, period=20, ma_type='SMA'):
        """
        Tính Moving Average (Đường trung bình động)
        
        Ý nghĩa:
        - Giá > MA: Xu hướng tăng
        - Giá < MA: Xu hướng giảm
        - MA ngắn vượt MA dài: Tín hiệu mua
        
        Args:
            df: DataFrame với cột 'close'
            period: Chu kỳ (vd: 20 = trung bình 20 phiên)
            ma_type: 'SMA' (đơn giản) hoặc 'EMA' (hàm mũ)
        
        Returns:
            Series: Giá trị MA
        """
        if ma_type == 'SMA':
            # SMA: Trung bình số học đơn giản
            ma = df['close'].rolling(window=period).mean()
        else:
            # EMA: Ưu tiên dữ liệu gần đây hơn
            ma = ta.ema(df['close'], length=period)
        
        return ma
    
    @staticmethod
    def calculate_rsi(df, period=14):
        """
        Tính RSI (Relative Strength Index)
        
        Ý nghĩa:
        - RSI > 70: Thị trường QUÁ MUA (overbought) → có thể giảm
        - RSI < 30: Thị trường QUÁ BÁN (oversold) → có thể tăng
        - RSI ~ 50: Thị trường cân bằng
        
        Args:
            df: DataFrame với cột 'close'
            period: Chu kỳ tính toán (thường 14)
        
        Returns:
            Series: Giá trị RSI (0-100)
        """
        rsi = ta.rsi(df['close'], length=period)
        return rsi
    
    @staticmethod
    def calculate_atr(df, period=14):
        """
        Tính ATR (Average True Range)
        
        Ý nghĩa:
        - ATR cao: Thị trường biến động mạnh (cần stop loss xa hơn)
        - ATR thấp: Thị trường ổn định
        - Dùng để đặt stop loss/take profit phù hợp
        
        Args:
            df: DataFrame với cột 'high', 'low', 'close'
            period: Chu kỳ tính toán
        
        Returns:
            Series: Giá trị ATR
        """
        atr = ta.atr(high=df['high'], low=df['low'], close=df['close'], length=period)
        return atr
    
    @staticmethod
    def get_all_indicators(df, ma_period=10, rsi_period=14, atr_period=14):
        """
        Tính tất cả chỉ số một lúc - hàm tiện ích
        
        Returns:
            dict: {
                'ma': giá trị MA cuối,
                'rsi': giá trị RSI cuối,
                'atr': giá trị ATR cuối,
                'current_price': giá hiện tại,
                'raw_data': DataFrame đầy đủ
            }
        """
        # Tính các chỉ số
        ma = TechnicalIndicators.calculate_ma(df, ma_period)
        rsi = TechnicalIndicators.calculate_rsi(df, rsi_period)
        atr = TechnicalIndicators.calculate_atr(df, atr_period)
        
        # Lấy giá trị mới nhất (cuối cùng)
        current_price = df['close'].iloc[-1]
        ma_value = ma.iloc[-1]
        rsi_value = rsi.iloc[-1]
        atr_value = atr.iloc[-1]
        
        # Tạo DataFrame đầy đủ để vẽ đồ thị
        result_df = df.copy()
        result_df['MA'] = ma
        result_df['RSI'] = rsi
        result_df['ATR'] = atr
        
        # Log dữ liệu cuối cùng
        print(result_df[['close', 'MA', 'RSI', 'ATR']].tail())
        
        return {
            'current_price': current_price,
            'ma': ma_value,
            'rsi': rsi_value,
            'atr': atr_value,
            'raw_data': result_df
        }

if __name__ == '__main__':
    # Test module với dữ liệu mẫu
    print("🧪 Testing Technical Indicators...")
    
    # Tạo dữ liệu mẫu
    import numpy as np
    dates = pd.date_range('2024-01-01', periods=100, freq='1H')
    df = pd.DataFrame({
        'close': 40000 + np.random.randn(100) * 100,
        'high': 40000 + np.random.randn(100) * 150,
        'low': 40000 + np.random.randn(100) * 150,
        'open': 40000 + np.random.randn(100) * 100
    })
    df.index = dates
    
    # Tính chỉ số
    indicators = TechnicalIndicators.get_all_indicators(df)
    
    print(f"\n📊 KẾT QUẢ:")
    print(f"💰 Giá hiện tại: ${indicators['current_price']:.2f}")
    print(f"📈 MA(10): ${indicators['ma']:.2f}")
    print(f"📊 RSI(14): {indicators['rsi']:.2f}")
    print(f"📉 ATR(14): ${indicators['atr']:.2f}")
    
    # Phân tích nhanh
    print(f"\n🔍 PHÂN TÍCH:")
    if indicators['rsi'] > 70:
        print("⚠️ RSI > 70: Thị trường QUÁ MUA - có thể giảm")
    elif indicators['rsi'] < 30:
        print("✅ RSI < 30: Thị trường QUÁ BÁN - có thể tăng")
    else:
        print("⚖️ RSI ổn định: Thị trường cân bằng")
    
    if indicators['atr'] > 200:
        print("⚠️ ATR cao: Biến động mạnh - cẩn thận!")

