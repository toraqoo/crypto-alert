import os
import requests
from datetime import datetime, timezone, timedelta

# ── 설정 ──────────────────────────────────────────────
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

KST = timezone(timedelta(hours=9))


# ── 데이터 수집 ───────────────────────────────────────
def get_usdt_krw() -> float:
    """업비트 USDT/KRW 현재가"""
    url = "https://api.upbit.com/v1/ticker?markets=KRW-USDT"
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    return float(res.json()[0]["trade_price"])


def get_usd_krw() -> float:
    """ExchangeRate-API USD/KRW 환율"""
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    return float(res.json()["rates"]["KRW"])


def calc_kimchi(usdt_krw: float, usd_krw: float) -> float:
    """김치프리미엄 (%)"""
    return (usdt_krw / usd_krw - 1) * 100


# ── 메시지 생성 ───────────────────────────────────────
def build_message(usdt_krw: float, usd_krw: float, kimchi: float) -> str:
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    emoji = "🔴" if kimchi >= 2 else "🟡" if kimchi >= 0 else "🟢"

    return (
        f"📊 *암호화폐 모닝 브리핑*\n"
        f"🕖 {now}\n"
        f"{'─' * 26}\n"
        f"💵 USDT/KRW  `{usdt_krw:>10,.1f}` 원\n"
        f"💱 USD/KRW   `{usd_krw:>10,.1f}` 원\n"
        f"{'─' * 26}\n"
        f"{emoji} 김치프리미엄  `{kimchi:>+.2f}%`\n"
    )


# ── 텔레그램 발송 ─────────────────────────────────────
def send_telegram(message: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }
    res = requests.post(url, json=payload, timeout=10)
    res.raise_for_status()
    print("✅ 텔레그램 발송 완료")


# ── 메인 ─────────────────────────────────────────────
def main():
    print("📡 데이터 수집 중...")
    usdt_krw = get_usdt_krw()
    usd_krw = get_usd_krw()
    kimchi = calc_kimchi(usdt_krw, usd_krw)

    print(f"  USDT/KRW  : {usdt_krw:,.1f}")
    print(f"  USD/KRW   : {usd_krw:,.1f}")
    print(f"  김치프리미엄: {kimchi:+.2f}%")

    message = build_message(usdt_krw, usd_krw, kimchi)
    send_telegram(message)


if __name__ == "__main__":
    main()
