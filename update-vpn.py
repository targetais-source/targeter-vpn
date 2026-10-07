import base64
import json
import requests

sources = [
    "https://vlessfo.ru",
    "https://mos.ru"
]

VPN_NAME = "TargeterVPN"
VPN_DESC = "впн от айса"
country_cache = {}

def get_flag_and_code(address):
    if not address or address in country_cache:
        return country_cache.get(address, "🌐 [UN]")
    try:
        res = requests.get(f"http://ip-api.com{address}?fields=status,countryCode", timeout=3).json()
        if res.get("status") == "success":
            code = res.get("countryCode", "")
            if len(code) == 2:
                flag = chr(0x1F1E6 + ord(code[0]) - 65) + chr(0x1F1E6 + ord(code[1]) - 65)
                res_str = f"{flag} [{code}]"
                country_cache[address] = res_str
                return res_str
    except Exception:
        pass
    country_cache[address] = "🌐 [UN]"
    return "🌐 [UN]"

def extract_address(config):
    try:
        if config.startswith("vmess://"):
            b64_str = config.split("vmess://")[1]
            b64_str += "=" * (-len(b64_str) % 4)
            decoded = base64.b64decode(b64_str).decode('utf-8', errors='ignore')
            data = json.loads(decoded)
            return data.get("add", "")
        
        clean = config.split("://")[1]
        if "@" in clean:
            clean = clean.split("@")[1]
        host_part = clean.split("/")[0].split("?")[0].split("#")[0]
        if ":" in host_part:
            if host_part.startswith("["):
                return host_part.split("]")[0].replace("[", "")
            return host_part.split(":")[0]
        return host_part
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
                base_config, sep, old_name = line.partition('#')
                
                addr = extract_address(base_config)
                flag_str = get_flag_and_code(addr)
                
                custom_name = f"{flag_str} {VPN_NAME}_{counter}"
                new_config = f"{base_config}#{custom_name}"
                new_configs.append(new_config)
                counter += 1
                
    except Exception as e:
        print(f"Ошибка при обработке источника {url}: {e}")

if new_configs:
    profile_header = f"#profile-title: {VPN_NAME}\n#profile-update-interval: 1\n#announce: {VPN_DESC}\n"
    plain_text_data = profile_header + '\n'.join(new_configs)
    
    with open("working_configs.txt", "w", encoding="utf-8") as f:
        f.write(plain_text_data)
        
    base64_data = base64.b64encode(plain_text_data.encode('utf-8')).decode('utf-8')
    with open("sub_base64.txt", "w", encoding="utf-8") as f:
        f.write(base64_data)
        
    print(f"Успешно сохранено {len(new_configs)} серверов.")
else:
    print("Ошибка: не удалось собрать сервера.")
