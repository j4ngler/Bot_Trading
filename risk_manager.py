"""
Module quản lý rủi ro và quản lý lệnh
- Tính toán khối lượng giao dịch
- Thiết lập StopLoss/TakeProfit
- Quản lý vị thế và rủi ro
"""

import config
from datetime import datetime


class RiskOrderManager:
    """
    Class quản lý rủi ro và đơn hàng
    
    Chức năng:
    1. Tính khối lượng giao dịch dựa trên rủi ro
    2. Đặt StopLoss và TakeProfit
    3. Kiểm tra điều kiện thực thi
    4. Quản lý vị thế và exposure
    """
    
    def __init__(self, account_balance=10000):
        """
        Khởi tạo Risk Manager
        
        Args:
            account_balance: Số dư tài khoản (USDT)
        """
        self.account_balance = account_balance
        self.risk_percent = config.RISK_PERCENTAGE
        self.stop_loss_percent = config.STOP_LOSS_PERCENT
        self.take_profit_percent = config.TAKE_PROFIT_PERCENT
        self.max_positions = config.MAX_POSITIONS
        
        print("✅ Risk & Order Manager đã sẵn sàng")
    
    def calculate_position_size(self, entry_price, signal, current_atr=None):
        """
        Tính khối lượng giao dịch dựa trên rủi ro
        
        Công thức:
        position_size = (account * risk_percent) / stop_loss_amount
        
        Args:
            entry_price: Giá vào lệnh
            signal: 'BUY' hoặc 'SELL'
            current_atr: Giá trị ATR hiện tại (tùy chọn)
        
        Returns:
            dict: {
                'quantity': số lượng,
                'risk_amount': số tiền rủi ro,
                'stop_loss': giá stop loss,
                'take_profit': giá take profit
            }
        """
        try:
            # Tính số tiền chấp nhận rủi ro
            risk_amount = self.account_balance * (self.risk_percent / 100)
            
            # Tính stop loss amount
            stop_loss_amount = entry_price * (self.stop_loss_percent / 100)
            
            # Tính khối lượng
            quantity = risk_amount / stop_loss_amount
            
            # Nếu có ATR, dùng ATR để điều chỉnh stop loss linh hoạt hơn
            if current_atr and current_atr > 0:
                # Dùng 2x ATR làm stop loss
                atr_stop_loss = current_atr * 2
                quantity = risk_amount / atr_stop_loss
                stop_loss_price = entry_price - atr_stop_loss if signal == 'BUY' else entry_price + atr_stop_loss
                take_profit_price = entry_price + (current_atr * 3) if signal == 'BUY' else entry_price - (current_atr * 3)
            else:
                # Dùng % cố định
                if signal == 'BUY':
                    stop_loss_price = entry_price * (1 - self.stop_loss_percent / 100)
                    take_profit_price = entry_price * (1 + self.take_profit_percent / 100)
                else:  # SELL
                    stop_loss_price = entry_price * (1 + self.stop_loss_percent / 100)
                    take_profit_price = entry_price * (1 - self.take_profit_percent / 100)
            
            result = {
                'quantity': round(quantity, 6),
                'risk_amount': round(risk_amount, 2),
                'entry_price': entry_price,
                'stop_loss': round(stop_loss_price, 2),
                'take_profit': round(take_profit_price, 2),
                'signal': signal,
                'timestamp': datetime.now()
            }
            
            print(f"\n💰 Tính toán vị thế:")
            print(f"   💵 Khối lượng: {result['quantity']}")
            print(f"   ⚠️ Rủi ro: ${result['risk_amount']:.2f} ({self.risk_percent}%)")
            print(f"   📉 Stop Loss: ${result['stop_loss']:.2f}")
            print(f"   📈 Take Profit: ${result['take_profit']:.2f}")
            
            return result
            
        except Exception as e:
            print(f"❌ Lỗi tính toán vị thế: {e}")
            return None
    
    def check_risk_conditions(self, indicators, advice):
        """
        Kiểm tra điều kiện rủi ro trước khi thực thi
        
        Args:
            indicators: Dữ liệu chỉ số kỹ thuật
            advice: Khuyến nghị từ ChatGPT
        
        Returns:
            tuple: (có thể thực thi: bool, lý do: str)
        """
        try:
            # 1. Kiểm tra RSI không quá cực
            rsi = indicators.get('rsi', 50)
            if rsi > 75:
                return False, "RSI quá cao (>75) - Thị trường quá mua"
            elif rsi < 25:
                return False, "RSI quá thấp (<25) - Thị trường quá bán"
            
            # 2. Kiểm tra độ tin cậy của AI
            confidence = advice.get('confidence', 0)
            if confidence < 60:
                return False, f"Độ tin cậy thấp ({confidence}%)"
            
            # 3. Kiểm tra ATR - biến động quá cao
            atr = indicators.get('atr', 0)
            current_price = indicators.get('current_price', 0)
            if current_price > 0 and atr / current_price > 0.05:  # ATR > 5% giá
                return False, "Biến động quá cao (ATR > 5% giá)"
            
            # 4. Kiểm tra xu hướng MA
            ma = indicators.get('ma', 0)
            current_price = indicators.get('current_price', 0)
            if advice['recommendation'] == 'BUY' and current_price < ma:
                return True, "Giá dưới MA - Có thể là cơ hội mua"
            elif advice['recommendation'] == 'SELL' and current_price > ma:
                return True, "Giá trên MA - Có thể bán được"
            
            return True, "Điều kiện rủi ro hợp lý"
            
        except Exception as e:
            print(f"❌ Lỗi kiểm tra điều kiện: {e}")
            return False, f"Lỗi: {e}"
    
    def calculate_risk_reward_ratio(self, entry, stop_loss, take_profit):
        """
        Tính tỷ lệ Risk/Reward
        
        Args:
            entry: Giá vào lệnh
            stop_loss: Giá stop loss
            take_profit: Giá take profit
        
        Returns:
            float: Tỷ lệ R/R
        """
        try:
            if stop_loss == 0:
                return 0
            
            risk = abs(entry - stop_loss)
            reward = abs(take_profit - entry)
            
            ratio = reward / risk if risk > 0 else 0
            
            return round(ratio, 2)
            
        except Exception as e:
            print(f"❌ Lỗi tính R/R: {e}")
            return 0
    
    def update_account_balance(self, new_balance):
        """Cập nhật số dư tài khoản"""
        self.account_balance = new_balance
    
    def set_risk_parameters(self, risk_percent=None, stop_loss=None, take_profit=None):
        """
        Điều chỉnh tham số rủi ro
        
        Args:
            risk_percent: % vốn rủi ro mỗi lệnh
            stop_loss: % stop loss
            take_profit: % take profit
        """
        if risk_percent:
            self.risk_percent = risk_percent
        if stop_loss:
            self.stop_loss_percent = stop_loss
        if take_profit:
            self.take_profit_percent = take_profit
        
        print(f"✅ Cập nhật tham số rủi ro:")
        print(f"   ⚠️ Rủi ro: {self.risk_percent}%")
        print(f"   📉 Stop Loss: {self.stop_loss_percent}%")
        print(f"   📈 Take Profit: {self.take_profit_percent}%")


if __name__ == '__main__':
    # Test module
    print("🧪 Testing Risk & Order Manager...")
    
    manager = RiskOrderManager(account_balance=10000)
    
    # Test tính toán vị thế
    print("\n📊 Test tính toán vị thế BUY:")
    position = manager.calculate_position_size(
        entry_price=43250.0,
        signal='BUY',
        current_atr=250.0
    )
    
    if position:
        print(f"\n✅ Kết quả:")
        print(f"   Khối lượng: {position['quantity']}")
        print(f"   Rủi ro: ${position['risk_amount']:.2f}")
        print(f"   Stop Loss: ${position['stop_loss']:.2f}")
        print(f"   Take Profit: ${position['take_profit']:.2f}")
        
        # Tính R/R ratio
        rr_ratio = manager.calculate_risk_reward_ratio(
            position['entry_price'],
            position['stop_loss'],
            position['take_profit']
        )
        print(f"   R/R Ratio: {rr_ratio}")

