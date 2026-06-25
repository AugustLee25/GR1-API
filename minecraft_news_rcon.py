#!/usr/bin/env python3
"""
Lấy tin HUST từ RSS và cập nhật bảng text_display trong Minecraft qua RCON.
Minecraft 1.20.5+: text component là NBT Compound (SNBT), không bọc trong chuỗi JSON.
Persistent Connection: HTTP Session (Keep-Alive) + RCON giữ kết nối xuyên suốt.
"""

from __future__ import annotations

import json
import socket
import sys
import time
from datetime import datetime
from typing import Any, List

# Tránh lỗi Unicode trên console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import requests
from bs4 import BeautifulSoup
from mcrcon import MCRcon

# --- Cấu hình ---
RSS_URL = "https://hust.edu.vn/vi/news/rss/"
NEWS_COUNT = 5
UPDATE_INTERVAL_SEC = 60

RCON_HOST = "127.0.0.1"
RCON_PORT = 25575
RCON_PASSWORD = "123456"

REQUEST_TIMEOUT = 20
HTTP_USER_AGENT = "Mozilla/5.0 (HustMinecraftNewsBot/3.0)"

RCON_RECONNECT_ERRORS = (socket.error, ConnectionError, BrokenPipeError, OSError)


def log_ok(message: str) -> None:
    print(f"[{timestamp()}] [THÀNH CÔNG] {message}")


def log_err(message: str) -> None:
    print(f"[{timestamp()}] [LỖI] {message}", file=sys.stderr)


def log_info(message: str) -> None:
    print(f"[{timestamp()}] [THÔNG TIN] {message}")


def log_latency(latency_ms: float) -> None:
    print(f"[{timestamp()}] [LATENCY] Thời gian trễ End-to-End: {latency_ms:.2f} ms")


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def fetch_latest_titles(
    session: requests.Session,
    url: str,
    count: int = NEWS_COUNT,
) -> List[str]:
    """Đọc RSS HUST qua persistent session và trả về danh sách tiêu đề mới nhất."""
    log_info(f"Đang tải RSS: {url}")
    response = session.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "xml")
    items = soup.find_all("item")

    if not items:
        raise ValueError("Không tìm thấy thẻ <item> nào trong RSS HUST.")

    titles: List[str] = []
    for item in items:
        if len(titles) >= count:
            break
        title_tag = item.find("title")
        if title_tag is None:
            continue
        title = title_tag.get_text(strip=True)
        if title:
            titles.append(title)

    if len(titles) < count:
        raise ValueError(
            f"Chỉ lấy được {len(titles)} tiêu đề, cần ít nhất {count} tin."
        )

    return titles


def build_text_component(titles: List[str]) -> dict[str, Any]:
    """
    Tạo NBT Compound text component (1.20.5+):
    - Dòng 1: đỏ, in đậm
    - 5 dòng tiếp: vàng, có gạch đầu dòng
    """
    extra: List[dict[str, Any]] = [
        {
            "text": "📣 TIN TỨC HUST MỚI NHẤT 📣\n",
            "color": "red",
            "bold": True,
        },
    ]
    for title in titles:
        extra.append({"text": f"- {title}\n", "color": "yellow"})

    return {"text": "", "extra": extra}


def build_data_modify_command(titles: List[str]) -> str:
    """
    Lệnh RCON: gán trực tiếp NBT Compound vào tag text (không bọc nháy đơn/kép).
    Dùng /execute as để cập nhật mọi text_display có tag hust_board.
    """
    component = build_text_component(titles)
    json_str = json.dumps(component, ensure_ascii=False, separators=(",", ":"))

    return (
        f"/execute as @e[type=text_display,tag=hust_board] run data modify entity @s "
        f"text set value {json_str}"
    )


def send_rcon_command(rcon_client: MCRcon, command: str) -> str:
    """Gửi lệnh RCON với cơ chế tự kết nối lại khi mất đường truyền."""
    try:
        return rcon_client.command(command)
    except RCON_RECONNECT_ERRORS as exc:
        log_info(f"Mất kết nối RCON ({type(exc).__name__}: {exc}), đang thử kết nối lại ...")
        rcon_client.connect()
        log_ok(f"Đã khôi phục kết nối RCON {RCON_HOST}:{RCON_PORT}")
        return rcon_client.command(command)


def update_text_display(titles: List[str], rcon_client: MCRcon) -> str:
    """Gửi lệnh cập nhật text_display qua kết nối RCON persistent."""
    command = build_data_modify_command(titles)

    print("-" * 58)
    log_info("Lệnh RCON sẽ gửi (kiểm tra trước khi chạy):")
    print(command)
    print("-" * 58)

    return send_rcon_command(rcon_client, command)


def run_update_cycle(session: requests.Session, rcon_client: MCRcon) -> bool:
    """Một lần cập nhật: RSS → text_display. Trả về True nếu thành công."""
    try:
        start_time = time.perf_counter()
        titles = fetch_latest_titles(session, RSS_URL, NEWS_COUNT)
        log_ok(f"Đã lấy {len(titles)} tiêu đề HUST:")
        for index, title in enumerate(titles, start=1):
            preview = title if len(title) <= 80 else f"{title[:77]}..."
            print(f"    {index}. {preview}")

        response = update_text_display(titles, rcon_client)
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        log_latency(latency_ms)

        log_info(f"Phản hồi Minecraft: {response!r}")

        if response and "No entity was found" in response:
            log_err(
                "Không tìm thấy text_display có tag=hust_board. "
                "Hãy tạo entity và gắn tag trước khi chạy script."
            )
            return False

        log_ok("Đã cập nhật bảng text_display (hust_board).")
        return True

    except requests.RequestException as exc:
        log_err(f"Không tải được RSS: {exc}")
    except ValueError as exc:
        log_err(str(exc))
    except RCON_RECONNECT_ERRORS:
        log_err(
            "Không kết nối được RCON. Kiểm tra server đang chạy và "
            "enable-rcon=true trong server.properties."
        )
    except Exception as exc:  # noqa: BLE001
        log_err(f"Lỗi không mong đợi: {type(exc).__name__}: {exc}")

    return False


def main() -> None:
    print("=" * 58)
    print("  HUST NEWS → MINECRAFT TEXT_DISPLAY (RCON)")
    print("  Định dạng: NBT Compound (Minecraft 1.20.5+)")
    print("  Kết nối: Persistent HTTP Session + Persistent RCON")
    print(f"  RSS: {RSS_URL}")
    print(f"  Cập nhật mỗi {UPDATE_INTERVAL_SEC} giây — Nhấn Ctrl+C để dừng")
    print("=" * 58)

    session = requests.Session()
    session.headers.update({"User-Agent": HTTP_USER_AGENT})

    rcon_client = MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT)

    try:
        log_info(f"Đang thiết lập kết nối RCON tới {RCON_HOST}:{RCON_PORT} ...")
        rcon_client.connect()
        log_ok(f"Đã kết nối RCON {RCON_HOST}:{RCON_PORT} (persistent)")

        cycle = 0
        while True:
            cycle += 1
            print("-" * 58)
            log_info(f"=== Chu kỳ cập nhật #{cycle} ===")

            success = run_update_cycle(session, rcon_client)
            if success:
                log_ok(f"Chu kỳ #{cycle} hoàn tất.")
            else:
                log_err(
                    f"Chu kỳ #{cycle} thất bại — sẽ thử lại sau {UPDATE_INTERVAL_SEC}s."
                )

            log_info(f"Chờ {UPDATE_INTERVAL_SEC} giây trước lần cập nhật tiếp theo ...")
            time.sleep(UPDATE_INTERVAL_SEC)

    finally:
        try:
            rcon_client.disconnect()
            log_info("Đã đóng kết nối RCON.")
        except Exception:  # noqa: BLE001
            pass
        session.close()
        log_info("Đã đóng HTTP session.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        log_info("Đã dừng bot (Ctrl+C). Tạm biệt!")
        sys.exit(0)
