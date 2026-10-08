import base64
import json
import requests

sources = [
    "https://sub.vlessfo.ru/vlessforu/working_configs.txt",
    "https://hub.mos.ru/akelladejavu/bunker/-/raw/main/WHITE_LIST.txt"
]

country_cache = {}

def get_flag(address):
    if not address or address in country_cache:
        return country_cache.get(address, "🌐 [UN]")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(f"https://ipapi.co/{address}/json/", headers=headers, timeout=1.5)
        if res.status_code == 200:
            data = res.json()
            code = data.get("country_code", "")
            if len(code) == 2:
                flag = chr(0x1F1E6 + ord(code[0]) - 65) + chr(0x1F1E6 + ord(code[1]) - 65)
                res_str = f"{flag} [{code}]"
                country_cache[address] = res_str
                return res_str
    except Exception:
        pass
    
    country_cache[address] = "🌐 [UN]"
    return "🌐 [UN]"

def extract_ip(config):
    try:
        if config.startswith("vmess://"):
            b64 = config[8:]
            b64 += "=" * (-len(b64) % 4)
            data = json.loads(base64.b64decode(b64.encode()).decode('utf-8', 'ignore'))
            return str(data.get("add", ""))
        
        clean = config.split("://")[1].split("@")[-1]
        host = clean.split("/")[0].split("?")[0].split("#")[0]
        return host.split(":")[0].replace("[", "").replace("]", "")
    except Exception:
        return ""

new_configs = []
counter = 1

for url in sources:
    try:
        print(f"Скачивание источника: {url}")
        response = requests.get(url, timeout=20)
        lines = response.text.splitlines()
        
        for line in lines:
            line = line.strip()
            if line.startswith(('vless://', 'vmess://', 'trojan://', 'ss://')):
                base_config = line.split('#')[0] if '#' in line else line
                
                try:
                    host = extract_ip(base_config)
                    flag_tag = get_flag(host)
                except Exception:
                    flag_tag = "🌐 [UN]"
                
                custom_name = f"{flag_tag} TargeterVPN_{counter}"
                new_config = f"{base_config}#{custom_name}"
                new_configs.append(new_config)
                counter += 1
                
    except Exception as e:
        print(f"Ошибка при обработке источника {url}: {e}")

if new_configs:
    plain_text_data = '\n'.join(new_configs)
    
    with open("working_configs.txt", "w", encoding="utf-8") as f:
        f.write(plain_text_data)
        
    base64_data = base64.b64encode(plain_text_data.encode('utf-8')).decode('utf-8')
    with open("sub_base64.txt", "w", encoding="utf-8") as f:
        f.write(base64_data)
        
    print(f"Успешно сохранено {len(new_configs)} серверов.")
else:
    print("Ошибка: не удалось собрать сервера.")
