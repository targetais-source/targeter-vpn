import os
import re
import socket
import time
import requests
from concurrent.futures import ThreadPoolExecutor

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

URLS = [
    "https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/main/proxy_all.txt",
]

def check_single_proxy(item):
    srv, prt, proto_type, full_url = item
    try:
        start = time.time()
        s = socket.create_connection((srv, int(prt)), timeout=1.5)
        s.close()
        ping = round((time.time() - start) * 1000)
        return {
            "url": full_url,
            "type": "MTProto" if proto_type == "proxy" else "SOCKS5",
            "ping": ping
        }
    except Exception:
        return None

def parse_proxies():
    candidates = []
    seen_urls = set()

    for url in URLS:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code != 200:
                continue
            
            lines = res.text.splitlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                match_tg = re.search(r'(t\.me|tg://)/(proxy|socks)\?([^#\s]+)', line)
                if match_tg:
                    proto_type = match_tg.group(2)
                    params = match_tg.group(3)
                    
                    server = re.search(r'server=([^&]+)', params)
                    port = re.search(r'port=([^&]+)', params)
                    
                    if server and port:
                        srv = server.group(1)
                        prt = port.group(1)
                        full_url = f"https://t.me/{proto_type}?{params}"
                        
                        if full_url not in seen_urls:
                            seen_urls.add(full_url)
                            candidates.append((srv, prt, proto_type, full_url))
        except Exception as e:
            print(f"Ошибка загрузки {url}: {e}")

    print(f"Найдено уникальных прокси для проверки: {len(candidates)}")

    # Многопоточная молниеносная проверка
    working_proxies = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = executor.map(check_single_proxy, candidates)
        for res in results:
            if res is not None:
                working_proxies.append(res)

    working_proxies.sort(key=lambda x: x["ping"])
    print(f"Успешно прошли проверку: {len(working_proxies)}")
    return working_proxies[:3]

def send_telegram_post(proxies):
    if not BOT_TOKEN or not CHAT_ID:
        raise ValueError("Секреты TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не заданы в Repository Secrets!")

    if not proxies:
        print("Внимание: Ни один прокси не ответил на пинг.")
        return

    text = (
        "⚡️ **Свежие прокси для Telegram**\n\n"
        "Если Telegram работает медленно, нажмите на любую из кнопок ниже для подключения в один клик:\n"
    )

    keyboard = []
    for idx, p in enumerate(proxies, 1):
        keyboard.append([{
            "text": f"🚀 Подключить {p['type']} #{idx} ({p['ping']} ms)",
            "url": p["url"]
        }])

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": keyboard
        }
    }

    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    res = requests.post(api_url, json=payload)
    res_data = res.json()
    print("Ответ Telegram API:", res_data)

    if not res_data.get("ok"):
        raise RuntimeError(f"Ошибка отправки в Telegram: {res_data.get('description')}")

if __name__ == "__main__":
    best_proxies = parse_proxies()
    send_telegram_post(best_proxies)
