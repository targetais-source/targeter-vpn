import base64
import json
import socket
import requests
import geoip2.database

sources = [
    "https://sub.vlessfo.ru/vlessforu/working_configs.txt",
    "https://hub.mos.ru/akelladejavu/bunker/-/raw/main/WHITE_LIST.txt"
]

country_cache = {}
ip_cache = {}

try:
    reader = geoip2.database.Reader('Country.mmdb')
except Exception:
    reader = None

def resolve_host_to_ip(host):
    if not host:
        return ""
    if host in ip_cache:
        return ip_cache[host]
    try:
        ip = socket.gethostbyname(host)
        ip_cache[host] = ip
        return ip
    except Exception:
        ip_cache[host] = host
        return host

def get_flag(address):
    if not address:
        return "🌐 [UN]"
    
    ip = resolve_host_to_ip(address)
    
    if ip in country_cache:
        return country_cache[ip]
    
    if reader:
        try:
            response = reader.country(ip)
            code = response.country.iso_code
            if code and len(code) == 2:
                flag = chr(0x1F1E6 + ord(code[0]) - 65) + chr(0x1F1E6 + ord(code[1]) - 65)
                res_str = f"{flag} [{code}]"
                country_cache[ip] = res_str
                country_cache[address] = res_str
                return res_str
        except Exception:
            pass

    country_cache[ip] = "🌐 [UN]"
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

if reader:
    reader.close()

if new_configs:
    sub_title = "TargeterVPN"
    sub_desc = "впн от айса"
    
    plain_text_data = f"#PROFILE-TITLE: {sub_title}\n" + '\n'.join(new_configs)
    
    with open("working_configs.txt", "w", encoding="utf-8") as f:
        f.write(plain_text_data)
        
    raw_b64 = base64.b64encode('\n'.join(new_configs).encode('utf-8')).decode('utf-8')
    base64_data = f"#profile-title: base64:{base64.b64encode(sub_title.encode('utf-8')).decode('utf-8')}\n" + raw_b64
    
    with open("sub_base64.txt", "w", encoding="utf-8") as f:
        f.write(base64_data)
        
    print(f"Успешно сохранено {len(new_configs)} серверов.")
else:
    print("Ошибка: не удалось собрать сервера.")
