import base64
import re
import requests

sources = [
    "https://vlessfo.ru",
    "https://mos.ru"
]

# Регулярное выражение для поиска эмодзи флагов стран
FLAG_RE = re.compile(r'[\U0001F1E6-\U0001F1FF]{2}')

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
                flag = ""
                if '#' in line:
                    parts = line.split('#')
                    base_config = parts[0]  # Берем саму ссылку на прокси
                    old_name = parts[1]     # Берем старое имя сервера
                    
                    # Ищем флаг в старом названии сервера
                    found_flags = FLAG_RE.findall(old_name)
                    if found_flags:
                        flag = found_flags[0]  # Берем первый найденный флаг
                else:
                    base_config = line
              
                # Формируем имя: добавляем флаг через пробел, если он нашелся
                if flag:
                    custom_name = f"TargeterVPN_{counter} {flag}"
                else:
                    custom_name = f"TargeterVPN_{counter}"
                    
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
