"""
Module tích hợp ChatGPT API để đưa ra khuyến nghị giao dịch
Phù hợp cho học sinh cấp 3 - AI phân tích thị trường
"""

from openai import OpenAI
from . import config
import json
import re


class ChatGPTAdvisor:
    """
    Class sử dụng ChatGPT để phân tích và đưa ra khuyến nghị
    
    Luồng hoạt động:
    1. Nhận dữ liệu kỹ thuật (MA, RSI, ATR)
    2. Tạo prompt thông minh
    3. Gửi đến ChatGPT API
    4. Parse kết quả (BUY/SELL/HOLD)
    5. Trả về khuyến nghị + lý do
    """
    
    def __init__(self):
        """Khởi tạo OpenAI client"""
        try:
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
            self.model = config.OPENAI_MODEL
            print("✅ ChatGPT Advisor đã sẵn sàng")
        except Exception as e:
            print(f"❌ Lỗi khởi tạo ChatGPT: {e}")
            print("💡 Hãy kiểm tra OPENAI_API_KEY trong file .env")
    
    def analyze_market(self, symbol, current_price, ma, rsi, atr):
        """
        Phân tích thị trường bằng ChatGPT
        
        Args:
            symbol: Mã giao dịch (vd: BTCUSDT)
            current_price: Giá hiện tại
            ma: Giá trị Moving Average
            rsi: Giá trị RSI
            atr: Giá trị ATR
        
        Returns:
            dict: {
                'recommendation': 'BUY'/'SELL'/'HOLD',
                'reason': 'Lý do giải thích',
                'confidence': 0-100 (độ tin cậy)
            }
        """
        try:
            # Tạo prompt từ template
            prompt = config.TRADING_PROMPT.format(
                symbol=symbol,
                current_price=current_price,
                ma_value=ma,
                rsi_value=rsi,
                atr_value=atr,
                ma_period=config.MA_PERIOD
            )
            
            # Gửi đến ChatGPT
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Bạn là chuyên gia phân tích thị trường tiền điện tử. Nhiệm vụ: phân tích dữ liệu kỹ thuật và đưa ra khuyến nghị: BUY, SELL, hoặc HOLD. Luôn nhắc nhở về rủi ro khi đầu tư."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            # Lấy kết quả
            advice_text = response.choices[0].message.content
            
            # Parse kết quả (tìm BUY/SELL/HOLD)
            recommendation = self._parse_recommendation(advice_text)
            confidence = self._extract_confidence(advice_text)
            
            result = {
                'recommendation': recommendation,
                'reason': advice_text,
                'confidence': confidence,
                'raw_response': advice_text
            }
            
            print(f"🤖 ChatGPT khuyến nghị: {recommendation}")
            return result
            
        except Exception as e:
            print(f"❌ Lỗi gọi ChatGPT API: {e}")
            return {
                'recommendation': 'HOLD',
                'reason': 'Không thể kết nối ChatGPT API',
                'confidence': 0
            }

    def chat_with_user(self, history, user_message, *, temperature=0.6, max_tokens=400):
        """Trả lời hội thoại tự nhiên với người dùng.

        Args:
            history (list[dict]): Danh sách tin nhắn hội thoại theo định dạng OpenAI
                (mỗi phần tử có `role` và `content`). Nên bắt đầu bằng thông điệp hệ thống.
            user_message (str): Nội dung người dùng muốn hỏi.
            temperature (float): Mức độ sáng tạo của mô hình.
            max_tokens (int): Số token tối đa trong câu trả lời.

        Returns:
            str: Phản hồi của ChatGPT.
        """

        if not hasattr(self, 'client') or self.client is None:
            raise RuntimeError("ChatGPT client chưa được khởi tạo. Kiểm tra OPENAI_API_KEY.")

        if not isinstance(history, list):
            raise ValueError("history phải là list messages")

        try:
            messages = history + [{"role": "user", "content": user_message}]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            reply = response.choices[0].message.content.strip()

            # Cập nhật hội thoại (giữ tối đa 20 lượt gần nhất để tránh tràn token)
            history.append({"role": "user", "content": user_message})
            history.append({"role": "assistant", "content": reply})
            if len(history) > 40:
                # Giữ lại thông điệp hệ thống và 38 tin nhắn cuối
                system_messages = [msg for msg in history if msg.get("role") == "system"]
                recent_messages = [msg for msg in history if msg.get("role") != "system"][-38:]
                history.clear()
                history.extend(system_messages + recent_messages)

            return reply

        except Exception as e:
            raise RuntimeError(f"Không thể trò chuyện với ChatGPT: {e}")
    
    def _parse_recommendation(self, text):
        """
        Tách khuyến nghị từ text ChatGPT
        
        Tìm từ khóa: BUY, SELL, HOLD (không phân biệt hoa thường)
        """
        text_upper = text.upper()
        
        if 'BUY' in text_upper or 'MUA' in text_upper:
            return 'BUY'
        elif 'SELL' in text_upper or 'BÁN' in text_upper:
            return 'SELL'
        else:
            return 'HOLD'
    
    def _extract_confidence(self, text):
        """
        Trích xuất độ tin cậy từ text (nếu có)
        Mặc định 70%
        """
        # Tìm số phần trăm
        percent_match = re.search(r'(\d+)%', text)
        if percent_match:
            return int(percent_match.group(1))
        return 70  # Mặc định
    

if __name__ == '__main__':
    # Test module
    print("🧪 Testing ChatGPT Advisor...")
    
    advisor = ChatGPTAdvisor()
    
    # Test với dữ liệu mẫu
    print("\n📊 Phân tích thị trường với ChatGPT...")
    result = advisor.analyze_market(
        symbol='BTCUSDT',
        current_price=43250.5,
        ma=42800.0,
        rsi=72.5,
        atr=250.0
    )
    
    print(f"\n🤖 KHUYẾN NGHỊ: {result['recommendation']}")
    print(f"💬 Lý do: {result['reason']}")
    print(f"📊 Độ tin cậy: {result['confidence']}%")

