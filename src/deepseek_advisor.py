"""
Module DeepSeek Advisor
-----------------------
Tích hợp DeepSeek API (OpenAI-compatible endpoint) để phân tích thị trường
và đưa ra khuyến nghị BUY / SELL / HOLD giống ChatGPTAdvisor.
"""

from __future__ import annotations

import json
from typing import List, Dict, Any

from openai import OpenAI

from . import config


class DeepSeekAdvisor:
    """
    Advisor sử dụng mô hình DeepSeek (qua API tương thích OpenAI).

    Cách dùng:
        advisor = DeepSeekAdvisor()
        advice = advisor.analyze_market(symbol, price, ma, rsi, atr)
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or getattr(config, "DEEPSEEK_API_KEY", None)
        self.base_url = base_url or getattr(config, "DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.model = model or getattr(config, "DEEPSEEK_MODEL", "deepseek-chat")

        if not self.api_key:
            raise RuntimeError("Thiếu DEEPSEEK_API_KEY trong config hoặc .env.")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        print("✅ DeepSeek Advisor đã sẵn sàng")

    def analyze_market(self, symbol: str, current_price: float, ma: float, rsi: float, atr: float) -> Dict[str, Any]:
        prompt = config.TRADING_PROMPT.format(
            symbol=symbol,
            current_price=current_price,
            ma_value=ma,
            rsi_value=rsi,
            atr_value=atr,
            ma_period=config.MA_PERIOD,
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Bạn là chuyên gia giao dịch dùng mô hình DeepSeek. "
                        "Phân tích dữ liệu kỹ thuật và đưa ra khuyến nghị BUY, SELL hoặc HOLD. "
                        "Luôn nhắc rằng đây là môi trường học tập Binance Testnet."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
            max_tokens=300,
        )

        advice_text = response.choices[0].message.content
        recommendation = self._parse_recommendation(advice_text)
        confidence = self._extract_confidence(advice_text)

        return {
            "recommendation": recommendation,
            "reason": advice_text,
            "confidence": confidence,
            "raw_response": advice_text,
        }

    def chat_with_user(self, history: List[Dict[str, str]], user_message: str,
                       temperature: float = 0.6, max_tokens: int = 400) -> str:
        if not isinstance(history, list):
            raise ValueError("history phải là list messages")

        messages = history + [{"role": "user", "content": user_message}]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        reply = response.choices[0].message.content.strip()
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": reply})
        if len(history) > 40:
            system_messages = [msg for msg in history if msg.get("role") == "system"]
            recent_messages = [msg for msg in history if msg.get("role") != "system"][-38:]
            history.clear()
            history.extend(system_messages + recent_messages)

        return reply

    @staticmethod
    def _parse_recommendation(text: str) -> str:
        text_upper = text.upper()
        if "BUY" in text_upper or "MUA" in text_upper:
            return "BUY"
        if "SELL" in text_upper or "BÁN" in text_upper:
            return "SELL"
        return "HOLD"

    @staticmethod
    def _extract_confidence(text: str) -> int:
        import re

        match = re.search(r"(\d+)%", text)
        if match:
            return int(match.group(1))
        return 70


if __name__ == "__main__":
    advisor = DeepSeekAdvisor()
    result = advisor.analyze_market("BTCUSDT", 43250.5, 42800.0, 72.5, 250.0)
    print(json.dumps(result, indent=2, ensure_ascii=False))

