"""Entry point mới cho Trading Bot.

Chạy `python app.py` để:
1. Khởi động bot giao dịch chạy liên tục (không cần menu lựa chọn).
2. Đồng thời mở phiên chat trực tiếp với trợ lý AI để giải đáp thắc mắc.

Yêu cầu:
- Đã cấu hình API key trong `.env` (OpenAI + Binance Testnet).
- Đã cài đặt các dependencies trong `requirements.txt`.

Lưu ý: Đây là công cụ giáo dục, chỉ sử dụng với Binance Testnet.
"""

from __future__ import annotations

import os
import signal
import threading
import time
from typing import List, Dict

from .main import TradingBot


# Thời gian chờ giữa các chu kỳ phân tích (phút)
# Lấy từ config nếu có, nếu không thì dùng 5 phút
try:
    from . import config
    DEFAULT_INTERVAL_MINUTES = config.TRADING_INTERVAL_MINUTES
except (ImportError, AttributeError):
    DEFAULT_INTERVAL_MINUTES = float(os.getenv("APP_TRADING_INTERVAL", "5"))


def trading_loop(bot: TradingBot, stop_event: threading.Event, interval_minutes: float) -> None:
    """Chạy chu kỳ phân tích + giao dịch liên tục cho tới khi stop_event được kích hoạt."""

    print("\n🚀 Bắt đầu chế độ AUTO TRADING (không cần menu).")
    print(f"⏱️ Chu kỳ phân tích: {interval_minutes} phút\n")

    try:
        while not stop_event.is_set():
            bot.run_once()

            # Đợi tới chu kỳ tiếp theo (có thể bị ngắt bởi stop_event)
            if stop_event.wait(interval_minutes * 60):
                break
    except Exception as exc:
        print(f"❌ Lỗi trong trading_loop: {exc}")
    finally:
        print("🔚 Đã dừng trading loop.")


def chat_loop(bot: TradingBot, stop_event: threading.Event) -> None:
    """Vòng lặp chat CLI với trợ lý AI."""

    if not hasattr(bot, "advisor") or bot.advisor is None:
        print("⚠️ Không thể khởi tạo phiên chat vì ChatGPT Advisor chưa sẵn sàng.")
        return

    history: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": (
                "Bạn là trợ lý giao dịch AI thân thiện, sử dụng tiếng Việt đơn giản,"
                " ưu tiên giải thích dễ hiểu cho học sinh cấp 3. Luôn nhắc nhở rằng"
                " đây là môi trường học tập với Binance Testnet và không đưa lời khuyên"
                " đầu tư thực tế."
            ),
        }
    ]

    instructions = (
        "\n💬 Phiên chat với trợ lý AI đã sẵn sàng!\n"
        "- Nhập câu hỏi của bạn và nhấn Enter để nhận câu trả lời.\n"
        "- Gõ `/help` để xem hướng dẫn, `/exit` hoặc `/quit` để thoát và dừng bot.\n"
        "- Gõ `/status` để xem nhắc nhở cách theo dõi hoạt động của bot.\n"
    )
    print(instructions)

    while not stop_event.is_set():
        try:
            user_input = input("Bạn: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n⚠️ Nhận tín hiệu dừng từ người dùng.")
            stop_event.set()
            break

        if not user_input:
            continue

        command = user_input.lower()
        if command in {"/exit", "/quit"}:
            print("👋 Tạm biệt! Đang dừng bot và phiên chat...")
            stop_event.set()
            break
        if command == "/help":
            print(instructions)
            continue
        if command == "/status":
            print(
                "\n📊 Bạn có thể theo dõi log ở `trading_logs.txt` hoặc xem báo cáo"
                " bằng cách chạy chức năng xuất báo cáo trong `reporting_monitoring.py`."
                " Bot vẫn đang tự động phân tích mỗi chu kỳ.\n"
            )
            continue

        try:
            reply = bot.advisor.chat_with_user(history, user_input)
            print(f"🤖 AI: {reply}\n")
        except RuntimeError as exc:
            print(f"❌ {exc}")
        except Exception as exc:  # Bảo vệ để vòng chat không bị văng
            print(f"❌ Lỗi khi trò chuyện với AI: {exc}")


def install_signal_handlers(stop_event: threading.Event) -> None:
    """Cho phép dừng ứng dụng bằng Ctrl+C khi chạy trên main thread."""

    def handler(signum, frame):  # pragma: no cover - khó test tự động
        print("\n⚠️ Nhận tín hiệu dừng, đang thoát...")
        stop_event.set()

    signal.signal(signal.SIGINT, handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, handler)


def main() -> None:
    """Start bot trong chế độ auto và mở phiên chat AI."""

    stop_event = threading.Event()
    install_signal_handlers(stop_event)

    bot = TradingBot()

    interval_minutes = max(0.5, DEFAULT_INTERVAL_MINUTES)

    trading_thread = threading.Thread(
        target=trading_loop,
        args=(bot, stop_event, interval_minutes),
        name="TradingLoop",
        daemon=True,
    )
    trading_thread.start()

    try:
        chat_loop(bot, stop_event)
    finally:
        stop_event.set()
        trading_thread.join(timeout=5)
        print("✅ Đã thoát khỏi ứng dụng app.py")


if __name__ == "__main__":
    main()

