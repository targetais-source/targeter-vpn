import os
import re
import socket
import time
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

URLS = [
    "https://raw.githubusercontent.com/kort0881/telegram-proxy-collector/refs/heads/main/proxy_all.txt",
]

def check_ping(host, port, timeout=2.0):
    try:
        start = time.time()
        s = socket.create_connection((host, int(port)), timeout=timeout)
        s.close()
        return round((time.time() - start) * 1000)
    except Exception:
        return None

def parse_proxies():
    working_proxies = []
    
    for url in URLS:
        try:
            res = requests.get(url, timeout=10)
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
                        ping = check_ping(srv, prt)
                        
                        if ping is not None:
                            full_url = f"https://t.me/{proto_type}?{params}"
                            proxy_type_str = "MTProto" if proto_type == "proxy" else "SOCKS5"
                            working_proxies.append({
                                "url": full_url,
                                "type": proxy_type_str,
                                "ping": ping
                            })
        except Exception as e:
            print(f"Ошибка получения {url}: {e}")

    working_proxies.sort(key=lambda x: x["ping"])
    
    unique_proxies = []
    seen_urls = set()
    for p in working_proxies:
        if p["url"] not in seen_urls:
            seen_urls.add(p["url"])
            unique_proxies.append(p)

    return unique_proxies[:3]

def send_telegram_post(proxies):
    if not BOT_TOKEN or not CHAT_ID:
        print("Ошибка: Секреты TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не найдены!")
        return

    if not proxies:
        print("Рабочих прокси не найдено.")
        return

    text = (
        "⚡️ **Свежие прокси для Telegram**\n\n"
        "Если Telegram тормозит, нажмите на кнопку ниже для подключения в один клик:\n"
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
    response = requests.post(api_url, json=payload)
    print("Ответ Telegram API:", response.json())

if __name__ == "__main__":
    best_proxies = parse_proxies()
    send_telegram_post(best_proxies)
